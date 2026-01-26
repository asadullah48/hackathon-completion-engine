'use client';

import { useState } from 'react';
import {
  BookOpen,
  Search,
  FileText,
  Code,
  Database,
  Globe,
  ArrowLeft,
  ChevronRight,
  ExternalLink,
} from 'lucide-react';

// Sample course materials structure
const COURSE_MATERIALS = {
  categories: [
    {
      id: 'fundamentals',
      name: 'Programming Fundamentals',
      icon: Code,
      color: 'blue',
      materials: [
        {
          id: '1',
          title: 'Variables and Data Types',
          description: 'Understanding how to store and manipulate data',
          topics: ['integers', 'strings', 'booleans', 'type conversion'],
        },
        {
          id: '2',
          title: 'Control Flow',
          description: 'Conditional statements and loops',
          topics: ['if/else', 'for loops', 'while loops', 'break/continue'],
        },
        {
          id: '3',
          title: 'Functions',
          description: 'Creating reusable code blocks',
          topics: ['parameters', 'return values', 'scope', 'recursion'],
        },
      ],
    },
    {
      id: 'data-structures',
      name: 'Data Structures',
      icon: Database,
      color: 'green',
      materials: [
        {
          id: '4',
          title: 'Arrays and Lists',
          description: 'Sequential data storage',
          topics: ['indexing', 'slicing', 'iteration', 'list comprehension'],
        },
        {
          id: '5',
          title: 'Dictionaries and Hash Maps',
          description: 'Key-value pair storage',
          topics: ['keys', 'values', 'hashing', 'collision handling'],
        },
        {
          id: '6',
          title: 'Trees and Graphs',
          description: 'Hierarchical and connected data',
          topics: ['binary trees', 'traversal', 'BFS', 'DFS'],
        },
      ],
    },
    {
      id: 'algorithms',
      name: 'Algorithms',
      icon: FileText,
      color: 'purple',
      materials: [
        {
          id: '7',
          title: 'Sorting Algorithms',
          description: 'Organizing data efficiently',
          topics: ['bubble sort', 'merge sort', 'quick sort', 'complexity'],
        },
        {
          id: '8',
          title: 'Searching Algorithms',
          description: 'Finding elements in data',
          topics: ['linear search', 'binary search', 'hash tables'],
        },
        {
          id: '9',
          title: 'Dynamic Programming',
          description: 'Solving complex problems by breaking them down',
          topics: ['memoization', 'tabulation', 'optimal substructure'],
        },
      ],
    },
    {
      id: 'web',
      name: 'Web Development',
      icon: Globe,
      color: 'orange',
      materials: [
        {
          id: '10',
          title: 'HTML & CSS Basics',
          description: 'Building web page structure and style',
          topics: ['elements', 'selectors', 'layout', 'responsive design'],
        },
        {
          id: '11',
          title: 'JavaScript Essentials',
          description: 'Adding interactivity to web pages',
          topics: ['DOM manipulation', 'events', 'async/await', 'fetch API'],
        },
        {
          id: '12',
          title: 'React Fundamentals',
          description: 'Building modern user interfaces',
          topics: ['components', 'state', 'props', 'hooks'],
        },
      ],
    },
  ],
};

export default function MaterialsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedMaterial, setSelectedMaterial] = useState<typeof COURSE_MATERIALS.categories[0]['materials'][0] | null>(null);

  // Filter materials based on search
  const filteredCategories = COURSE_MATERIALS.categories.map((category) => ({
    ...category,
    materials: category.materials.filter(
      (material) =>
        material.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        material.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        material.topics.some((topic) => topic.toLowerCase().includes(searchQuery.toLowerCase()))
    ),
  })).filter((category) => category.materials.length > 0);

  const getColorClasses = (color: string) => {
    const colors: Record<string, { bg: string; text: string; border: string }> = {
      blue: { bg: 'bg-blue-100', text: 'text-blue-600', border: 'border-blue-200' },
      green: { bg: 'bg-green-100', text: 'text-green-600', border: 'border-green-200' },
      purple: { bg: 'bg-purple-100', text: 'text-purple-600', border: 'border-purple-200' },
      orange: { bg: 'bg-orange-100', text: 'text-orange-600', border: 'border-orange-200' },
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <a
            href="/"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-800 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Chat
          </a>
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-indigo-600" />
            Course Materials
          </h1>
          <p className="text-gray-600 mt-2">
            Browse learning resources and ask the AI about any topic
          </p>
        </div>

        {/* Search */}
        <div className="mb-8">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search materials, topics, concepts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Material Detail View */}
        {selectedMaterial ? (
          <div className="bg-white rounded-xl shadow-lg p-8">
            <button
              onClick={() => setSelectedMaterial(null)}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-800 mb-6"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Materials
            </button>

            <h2 className="text-2xl font-bold text-gray-800 mb-2">{selectedMaterial.title}</h2>
            <p className="text-gray-600 mb-6">{selectedMaterial.description}</p>

            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Topics Covered</h3>
              <div className="flex flex-wrap gap-2">
                {selectedMaterial.topics.map((topic, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-sm"
                  >
                    {topic}
                  </span>
                ))}
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Need Help?</h3>
              <p className="text-gray-600 mb-4">
                Ask the Course Companion AI about any of these topics. Remember, the AI will guide
                you to understand concepts through Socratic questioning.
              </p>
              <a
                href={`/?topic=${encodeURIComponent(selectedMaterial.title)}`}
                className="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Ask About This Topic
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          </div>
        ) : (
          /* Categories Grid */
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredCategories.map((category) => {
              const Icon = category.icon;
              const colors = getColorClasses(category.color);

              return (
                <div key={category.id} className="bg-white rounded-xl shadow-lg overflow-hidden">
                  <div className={`p-4 ${colors.bg} border-b ${colors.border}`}>
                    <div className="flex items-center gap-3">
                      <Icon className={`w-6 h-6 ${colors.text}`} />
                      <h2 className="text-lg font-semibold text-gray-800">{category.name}</h2>
                    </div>
                  </div>

                  <div className="p-4">
                    <div className="space-y-3">
                      {category.materials.map((material) => (
                        <button
                          key={material.id}
                          onClick={() => setSelectedMaterial(material)}
                          className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors text-left group"
                        >
                          <div>
                            <p className="font-medium text-gray-800 group-hover:text-indigo-600">
                              {material.title}
                            </p>
                            <p className="text-sm text-gray-500">{material.description}</p>
                          </div>
                          <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-indigo-600" />
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* No Results */}
        {searchQuery && filteredCategories.length === 0 && (
          <div className="text-center py-12">
            <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-800 mb-2">No materials found</h3>
            <p className="text-gray-600">
              Try a different search term or ask the AI about this topic directly.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
