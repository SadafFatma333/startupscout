import React from 'react';

interface DemoCardsProps {
  onQuestionClick: (question: string) => void;
  isVisible: boolean;
}

const DEMO_QUESTIONS = [
  "What helped teams get their first 100 active users?",
  "How do early startups choose their first price?", 
  "What convinced investors to write the first check (pre-seed/seed)?",
  "What small onboarding change improved sign-ups?"
];

const DemoCards: React.FC<DemoCardsProps> = ({ onQuestionClick, isVisible }) => {
  console.log('DemoCards render:', { isVisible }); // Debug log
  
  if (!isVisible) {
    console.log('DemoCards not visible, returning null');
    return null;
  }

  console.log('DemoCards rendering cards');

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      style={{ zIndex: 9999 }}
    >
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-y-auto">
        <div className="p-6">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Welcome to StartupScout! 🚀
            </h2>
            <p className="text-gray-600">
              Try one of these popular questions or ask your own:
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {DEMO_QUESTIONS.map((question, index) => (
              <button
                key={index}
                onClick={() => {
                  console.log('Demo question clicked:', question);
                  onQuestionClick(question);
                }}
                className="p-4 text-left bg-gradient-to-br from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 border border-blue-200 rounded-xl transition-all duration-200 hover:shadow-lg hover:scale-105 group"
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-semibold group-hover:bg-blue-600 transition-colors">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <p className="text-gray-800 font-medium group-hover:text-blue-800 transition-colors">
                      {question}
                    </p>
                  </div>
                </div>
                <div className="mt-2 text-xs text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity">
                  Click to see answer →
                </div>
              </button>
            ))}
          </div>
          
          <div className="text-center">
            <p className="text-sm text-gray-500 mb-2">
              Or type your own question below:
            </p>
            <div className="w-8 h-1 bg-blue-300 rounded mx-auto"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemoCards;
