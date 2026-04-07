import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

def train_gemma4():
    """
    Step-by-step script to fine-tune Gemma 4 for Pharmacogenomics.
    """
    # -------------------------------------------------------------------------
    # STEP 1: Model & Dataset Selection
    # -------------------------------------------------------------------------
    print("=== STEP 1: Setting up configurations ===")
    # Note: If Gemma 4 is very new, ensure you have the latest 'transformers' library.
    # You can change this to 'google/gemma-2-9b-it' if 'gemma-4' is not yet on HuggingFace.
    model_id = "google/gemma-4-8b-it"  
    dataset_file = "pharmgeno_dataset.jsonl" 
    
    # -------------------------------------------------------------------------
    # STEP 2: Configure Quantization (Making it fit on a PC)
    # -------------------------------------------------------------------------
    print("=== STEP 2: Configuring Quantization (4-bit) ===")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )
    
    # -------------------------------------------------------------------------
    # STEP 3: Load the Model & Tokenizer
    # -------------------------------------------------------------------------
    print(f"=== STEP 3: Loading {model_id} ===")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        tokenizer.pad_token = tokenizer.eos_token 
        
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=bnb_config,
            device_map="auto"
        )
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Tip: Make sure you are logged into HuggingFace (huggingface-cli login) and have access to the Gemma model.")
        return
    
    # -------------------------------------------------------------------------
    # STEP 4: Configure LoRA (Fine-tuning only ~1-2% of weights)
    # -------------------------------------------------------------------------
    print("=== STEP 4: Applying LoRA Configuration ===")
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, peft_config)
    
    # -------------------------------------------------------------------------
    # STEP 5: Load and Format Dataset
    # -------------------------------------------------------------------------
    print("=== STEP 5: Loading Dataset ===")
    if not os.path.exists(dataset_file):
        print(f"ERROR: Dataset '{dataset_file}' not found.")
        print("Please run your data generation script first to create this file.")
        return
        
    dataset = load_dataset("json", data_files=dataset_file, split="train")
    
    def format_gemma_prompt(example):
        # Wraps your data in Gemma's instruction format
        user_prompt = example['prompt']
        response = example['ideal_json_response']
        text = f"<start_of_turn>user\n{user_prompt}<end_of_turn>\n<start_of_turn>model\n{response}<end_of_turn>"
        return {"text": text}
        
    dataset = dataset.map(format_gemma_prompt)
    
    # -------------------------------------------------------------------------
    # STEP 6: Training Setup
    # -------------------------------------------------------------------------
    print("=== STEP 6: Setting up Training Loop ===")
    training_args = TrainingArguments(
        output_dir="./gemma4-pharmgeno-checkpoints",
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        optim="paged_adamw_32bit",
        save_steps=100,
        logging_steps=10,
        learning_rate=2e-4,
        num_train_epochs=3,
        bf16=torch.cuda.is_bf16_supported(),
        group_by_length=True,
        report_to="none" # Change to "wandb" if you want to track progress online
    )
    
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        dataset_text_field="text",
        max_seq_length=2048,
        tokenizer=tokenizer,
        args=training_args,
    )
    
    print("Starting training... (Grab a coffee, this takes a while)")
    trainer.train()
    
    # -------------------------------------------------------------------------
    # STEP 7: Save the Result
    # -------------------------------------------------------------------------
    print("=== STEP 7: Saving your specialized model ===")
    final_path = "./gemma4-pharmgeno-final"
    trainer.model.save_pretrained(final_path)
    tokenizer.save_pretrained(final_path)
    print(f"COMPLETE! Your model is saved at {final_path}")

if __name__ == "__main__":
    train_gemma4()
