'use client';

import { createContext, useContext, useEffect, useRef } from 'react';

// Define the type for our shortcut context
interface ShortcutContextType {
  registerShortcut: (keys: string[], handler: () => void, description?: string) => void;
  unregisterShortcut: (keys: string[]) => void;
}

// Create the context
const ShortcutContext = createContext<ShortcutContextType | undefined>(undefined);

// Helper function to normalize key combinations
const normalizeKeys = (keys: string[]): string => {
  return keys.map(k => k.toLowerCase()).sort().join('+');
};

// Shortcut Provider Component
interface ShortcutProviderProps {
  children: React.ReactNode;
}

export const ShortcutProvider: React.FC<ShortcutProviderProps> = ({ children }) => {
  const shortcutsRef = useRef<Map<string, { handler: () => void; description?: string }>>(new Map());

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Build the key combination string
      const keys: string[] = [];
      if (event.ctrlKey) keys.push('ctrl');
      if (event.shiftKey) keys.push('shift');
      if (event.altKey) keys.push('alt');
      if (event.metaKey) keys.push('meta'); // Cmd key on Mac
      
      // Add the main key
      const mainKey = event.key.toLowerCase();
      if (mainKey.length === 1 || /^[0-9]$/.test(mainKey) || ['enter', 'escape', 'backspace', 'delete', 'arrowup', 'arrowdown', 'arrowleft', 'arrowright'].includes(mainKey)) {
        keys.push(mainKey);
      }

      const keyCombination = normalizeKeys(keys);

      // Find and execute the corresponding handler
      const shortcut = shortcutsRef.current.get(keyCombination);
      if (shortcut) {
        event.preventDefault();
        shortcut.handler();
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const registerShortcut = (keys: string[], handler: () => void, description?: string) => {
    const normalizedKey = normalizeKeys(keys);
    shortcutsRef.current.set(normalizedKey, { handler, description });
  };

  const unregisterShortcut = (keys: string[]) => {
    const normalizedKey = normalizeKeys(keys);
    shortcutsRef.current.delete(normalizedKey);
  };

  return (
    <ShortcutContext.Provider value={{ registerShortcut, unregisterShortcut }}>
      {children}
    </ShortcutContext.Provider>
  );
};

// Custom hook to use shortcuts
export const useShortcuts = () => {
  const context = useContext(ShortcutContext);
  if (!context) {
    throw new Error('useShortcuts must be used within a ShortcutProvider');
  }
  return context;
};

// Component to display available shortcuts
export const ShortcutGuide: React.FC = () => {
  const { registerShortcut, unregisterShortcut } = useShortcuts();
  
  useEffect(() => {
    const showGuide = () => {
      alert(`
Keyboard Shortcuts:
- Ctrl + E: Edit selected todo
- Ctrl + D: Delete selected todo
- Ctrl + N: Create new todo
- Ctrl + Shift + N: Create new team
- Ctrl + K: Show shortcuts
- Esc: Close modals
      `);
    };

    registerShortcut(['ctrl', 'k'], showGuide, 'Show keyboard shortcuts');
    
    return () => {
      unregisterShortcut(['ctrl', 'k']);
    };
  }, [registerShortcut, unregisterShortcut]);

  return null;
};