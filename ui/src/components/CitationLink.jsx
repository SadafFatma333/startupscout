import React, { useEffect } from "react";

export default function CitationLink({ html, answerId }) {
  useEffect(() => {
    // Add smooth scroll behavior to citation links
    const handleCitationClick = (e) => {
      const target = e.target;
      if (target.classList.contains('cite')) {
        e.preventDefault();
        const href = target.getAttribute('href');
        if (href && href.startsWith('#ref-')) {
          // Find the target element within the current answer context
          const answerCard = target.closest('.answerCard');
          if (answerCard) {
            const targetElement = answerCard.querySelector(href);
            if (targetElement) {
              // Smooth scroll to target
              targetElement.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
              });
              
              // Add highlight effect
              targetElement.classList.add('highlighted');
              setTimeout(() => {
                targetElement.classList.remove('highlighted');
              }, 2000);
            }
          }
        }
      }
    };

    document.addEventListener('click', handleCitationClick);
    return () => document.removeEventListener('click', handleCitationClick);
  }, []);

  // html is already linkified via linkifyCitations
  return <span dangerouslySetInnerHTML={{ __html: html }} />;
}
