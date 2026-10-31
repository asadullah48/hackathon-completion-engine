import { useState } from 'react';
import { Download, Upload, FileJson, FileSpreadsheet } from 'lucide-react';
import { exportTodos, exportTodosToCSV, importTodos } from '@/lib/exportImportUtils';
import { useTodoStore } from '@/lib/store';
import { Todo } from '@/lib/types';

interface ExportImportPanelProps {
  todos: Todo[];
}

export default function ExportImportPanel({ todos }: ExportImportPanelProps) {
  const [isImporting, setIsImporting] = useState(false);
  const [importStatus, setImportStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const handleExportJSON = () => {
    exportTodos(todos, `todos-backup-${new Date().toISOString().slice(0, 10)}.json`);
  };

  const handleExportCSV = () => {
    exportTodosToCSV(todos, `todos-backup-${new Date().toISOString().slice(0, 10)}.csv`);
  };

  const handleFileImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsImporting(true);
    setImportStatus(null);

    try {
      const importedTodos = await importTodos(file);
      
      // Add imported todos to the store
      importedTodos.forEach(todo => {
        useTodoStore.getState().createTodo(todo);
      });
      
      setImportStatus({
        type: 'success',
        message: `Successfully imported ${importedTodos.length} todos!`
      });
    } catch (error) {
      setImportStatus({
        type: 'error',
        message: error instanceof Error ? error.message : 'Failed to import todos'
      });
    } finally {
      setIsImporting(false);
      // Reset the file input
      if (event.target) {
        event.target.value = '';
      }
    }
  };

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Export & Import</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Export Section */}
        <div>
          <h3 className="font-medium text-gray-800 mb-3">Export Todos</h3>
          <p className="text-sm text-gray-600 mb-4">Save your todos to a file for backup or transfer</p>
          
          <div className="flex flex-col gap-3">
            <button
              onClick={handleExportJSON}
              disabled={todos.length === 0}
              className={`flex items-center justify-center gap-2 px-4 py-2 rounded-lg border ${
                todos.length === 0 
                  ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed' 
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}
            >
              <Download className="w-4 h-4" />
              Export as JSON
            </button>
            
            <button
              onClick={handleExportCSV}
              disabled={todos.length === 0}
              className={`flex items-center justify-center gap-2 px-4 py-2 rounded-lg border ${
                todos.length === 0 
                  ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed' 
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}
            >
              <FileSpreadsheet className="w-4 h-4" />
              Export as CSV
            </button>
          </div>
        </div>
        
        {/* Import Section */}
        <div>
          <h3 className="font-medium text-gray-800 mb-3">Import Todos</h3>
          <p className="text-sm text-gray-600 mb-4">Load todos from a previously exported file</p>
          
          <div className="flex flex-col gap-3">
            <label className="flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer">
              <Upload className="w-4 h-4" />
              <span>Import from JSON/CSV</span>
              <input
                type="file"
                accept=".json,.csv"
                onChange={handleFileImport}
                className="hidden"
                disabled={isImporting}
              />
            </label>
            
            {isImporting && (
              <div className="text-sm text-blue-600 flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                Processing file...
              </div>
            )}
            
            {importStatus && (
              <div className={`text-sm p-2 rounded ${
                importStatus.type === 'success' 
                  ? 'bg-green-50 text-green-700 border border-green-200' 
                  : 'bg-red-50 text-red-700 border border-red-200'
              }`}>
                {importStatus.message}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}