'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Plus, X, Pill, Loader2 } from 'lucide-react';

interface MedicationInputProps {
  medications: string[];
  onAdd: (medication: string) => void;
  onRemove: (medication: string) => void;
}

// Common medications for offline fallback
const COMMON_MEDICATIONS = [
  "Acetaminophen", "Ibuprofen", "Aspirin", "Naproxen",
  "Omeprazole", "Pantoprazole", "Esomeprazole", "Lansoprazole",
  "Lisinopril", "Losartan", "Amlodipine", "Metoprolol", "Atenolol",
  "Metformin", "Glipizide", "Sitagliptin", "Empagliflozin",
  "Atorvastatin", "Simvastatin", "Rosuvastatin", "Pravastatin",
  "Sertraline", "Fluoxetine", "Escitalopram", "Citalopram", "Paroxetine",
  "Amoxicillin", "Azithromycin", "Ciprofloxacin", "Doxycycline",
  "Warfarin", "Clopidogrel", "Apixaban", "Rivaroxaban",
  "Gabapentin", "Pregabalin", "Tramadol", "Oxycodone", "Hydrocodone",
  "Levothyroxine", "Prednisone", "Albuterol", "Montelukast",
  "Tamoxifen", "Codeine", "Morphine", "Fentanyl",
  "Venlafaxine", "Duloxetine", "Bupropion", "Trazodone"
];

export default function MedicationInput({ medications, onAdd, onRemove }: MedicationInputProps) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const searchMedications = useCallback(async (searchQuery: string) => {
    if (searchQuery.length < 2) {
      setSuggestions([]);
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`/api/medications/search?q=${encodeURIComponent(searchQuery)}`);
      if (response.ok) {
        const data = await response.json();
        const results = data.results?.map((r: any) => r.name) || [];
        setSuggestions(results);
      } else {
        // Fallback to local search
        const filtered = COMMON_MEDICATIONS.filter(med =>
          med.toLowerCase().includes(searchQuery.toLowerCase())
        );
        setSuggestions(filtered.slice(0, 10));
      }
    } catch {
      // Fallback to local search
      const filtered = COMMON_MEDICATIONS.filter(med =>
        med.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setSuggestions(filtered.slice(0, 10));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      searchMedications(query);
    }, 300);

    return () => clearTimeout(timer);
  }, [query, searchMedications]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleAddMedication = (medication: string) => {
    if (medication && !medications.includes(medication)) {
      onAdd(medication);
      setQuery('');
      setSuggestions([]);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (suggestions.length > 0) {
        handleAddMedication(suggestions[0]);
      } else if (query.trim()) {
        handleAddMedication(query.trim());
      }
    }
  };

  return (
    <div className="space-y-4">
      <div ref={containerRef} className="relative">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setShowSuggestions(true)}
            onKeyDown={handleKeyDown}
            placeholder="Search for a medication..."
            className="w-full pl-12 pr-12 py-4 rounded-xl bg-slate-800 border border-slate-700 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 outline-none transition-all text-white placeholder-slate-500"
          />
          {isLoading && (
            <Loader2 className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-cyan-400 animate-spin" />
          )}
        </div>

        {/* Suggestions dropdown */}
        <AnimatePresence>
          {showSuggestions && suggestions.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute z-10 w-full mt-2 py-2 rounded-xl bg-slate-800 border border-slate-700 shadow-xl max-h-60 overflow-auto"
            >
              {suggestions.map((suggestion, index) => (
                <button
                  key={suggestion}
                  onClick={() => handleAddMedication(suggestion)}
                  className="w-full px-4 py-3 text-left hover:bg-slate-700 transition-colors flex items-center gap-3"
                >
                  <Pill className="w-4 h-4 text-cyan-400" />
                  <span>{suggestion}</span>
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Selected medications */}
      <div className="min-h-[120px] p-4 rounded-xl bg-slate-800/50 border border-slate-700">
        {medications.length === 0 ? (
          <div className="h-full flex items-center justify-center text-slate-500">
            <Pill className="w-5 h-5 mr-2" />
            Add your medications above
          </div>
        ) : (
          <div className="flex flex-wrap gap-2">
            <AnimatePresence>
              {medications.map((medication) => (
                <motion.div
                  key={medication}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                >
                  <Pill className="w-4 h-4" />
                  <span>{medication}</span>
                  <button
                    onClick={() => onRemove(medication)}
                    className="p-0.5 rounded-full hover:bg-cyan-500/30 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Quick add suggestions */}
      <div>
        <p className="text-sm text-slate-500 mb-2">Common medications:</p>
        <div className="flex flex-wrap gap-2">
          {['Metformin', 'Lisinopril', 'Atorvastatin', 'Omeprazole', 'Sertraline'].map((med) => (
            <button
              key={med}
              onClick={() => handleAddMedication(med)}
              disabled={medications.includes(med)}
              className="px-3 py-1 rounded-full text-sm bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              + {med}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
