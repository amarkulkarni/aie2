import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedPrompts, setSuggestedPrompts] = useState([]);
  const [conversationEnded, setConversationEnded] = useState(false);
  const messagesEndRef = useRef(null);

  // Function to format agent response with proper structure
  const formatAgentResponse = (content) => {
    if (!content) return [];
    
    const elements = [];
    const lines = content.split('\n');
    let currentSection = null;
    let currentSubsection = null;
    let currentList = [];
    let listLevel = 0;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      if (!line) continue;
      
      // Main headings (## or **Title**)
      if (line.startsWith('##') || (line.startsWith('**') && line.endsWith('**') && line.length > 4)) {
        // Close any open lists
        if (currentList.length > 0) {
          elements.push({
            className: `list-level-${listLevel}`,
            content: <ul>{currentList.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
          });
          currentList = [];
          listLevel = 0;
        }
        
        const title = line.replace(/^##\s*/, '').replace(/\*\*/g, '');
        elements.push({
          className: 'main-heading',
          content: <h2>{title}</h2>
        });
        currentSection = title;
        currentSubsection = null;
      }
      // Subheadings (### or **Subtitle**)
      else if (line.startsWith('###') || (line.startsWith('**') && line.endsWith('**') && line.length > 4 && !line.includes(':'))) {
        // Close any open lists
        if (currentList.length > 0) {
          elements.push({
            className: `list-level-${listLevel}`,
            content: <ul>{currentList.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
          });
          currentList = [];
          listLevel = 0;
        }
        
        const subtitle = line.replace(/^###\s*/, '').replace(/\*\*/g, '');
        elements.push({
          className: 'sub-heading',
          content: <h3>{subtitle}</h3>
        });
        currentSubsection = subtitle;
      }
      // Wikipedia sections (### Wikipedia:)
      else if (line.startsWith('### Wikipedia:')) {
        // Close any open lists
        if (currentList.length > 0) {
          elements.push({
            className: `list-level-${listLevel}`,
            content: <ul>{currentList.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
          });
          currentList = [];
          listLevel = 0;
        }
        
        const title = line.replace(/^### Wikipedia:\s*/, '');
        elements.push({
          className: 'wikipedia-heading',
          content: <h3>📚 Wikipedia: {title}</h3>
        });
        currentSubsection = title;
      }
      // List items (- or • or numbered)
      else if (line.match(/^[-•]\s+/) || line.match(/^\d+\.\s+/)) {
        const listItem = line.replace(/^[-•]\s+/, '').replace(/^\d+\.\s+/, '');
        
        // Check for bold text in list items
        const formattedItem = listItem.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        currentList.push(<span dangerouslySetInnerHTML={{ __html: formattedItem }} />);
        listLevel = 1;
      }
      // Sub-list items (indented)
      else if (line.match(/^\s+[-•]\s+/) || line.match(/^\s+\d+\.\s+/)) {
        const listItem = line.replace(/^\s+[-•]\s+/, '').replace(/^\s+\d+\.\s+/, '');
        const formattedItem = listItem.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        currentList.push(<span dangerouslySetInnerHTML={{ __html: formattedItem }} />);
        listLevel = 2;
      }
      // Regular paragraphs
      else {
        // Close any open lists
        if (currentList.length > 0) {
          elements.push({
            className: `list-level-${listLevel}`,
            content: <ul>{currentList.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
          });
          currentList = [];
          listLevel = 0;
        }
        
        // Format bold text and other markdown
        const formattedLine = line
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
          .replace(/`(.*?)`/g, '<code>$1</code>');
        
        elements.push({
          className: 'paragraph',
          content: <p dangerouslySetInnerHTML={{ __html: formattedLine }} />
        });
      }
    }
    
    // Close any remaining lists
    if (currentList.length > 0) {
      elements.push({
        className: `list-level-${listLevel}`,
        content: <ul>{currentList.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
      });
    }
    
    return elements;
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetchSuggestedPrompts();
  }, []);

  const fetchSuggestedPrompts = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/suggested-prompts`);
      setSuggestedPrompts(response.data.prompts);
    } catch (error) {
      console.error('Error fetching suggested prompts:', error);
    }
  };

  const sendMessage = async (messageText) => {
    if (!messageText.trim() || isLoading || conversationEnded) return;

    const userMessage = { role: 'user', content: messageText };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        message: messageText
      });

      const agentMessage = {
        role: 'assistant',
        content: response.data.response,
        tools_used: response.data.tools_used
      };

      setMessages(prev => [...prev, agentMessage]);

      if (response.data.conversation_ended) {
        setConversationEnded(true);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputMessage);
  };

  const handleSuggestedPrompt = (prompt) => {
    sendMessage(prompt);
  };


  const resetConversation = () => {
    setMessages([]);
    setConversationEnded(false);
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🤖 AMA Agent</h1>
        <p>Ask me anything!</p>
      </header>

      <div className="chat-container">
        {/* Always visible suggested prompts */}
        <div className="suggested-prompts-container">
          <h3>💡 Suggested Prompts</h3>
          <div className="suggested-prompts">
            {suggestedPrompts.map((prompt, index) => (
              <button
                key={index}
                className="suggested-prompt-btn"
                onClick={() => handleSuggestedPrompt(prompt)}
                disabled={isLoading || conversationEnded}
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        <div className="messages-container">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                <div className="message-text">
                  {formatAgentResponse(message.content).map((element, i) => (
                    <div key={i} className={element.className}>
                      {element.content}
                    </div>
                  ))}
                  
                  {message.tools_used && message.tools_used.length > 0 && (
                    <div className="tools-used-section">
                      <h4>🔧 Tools Used</h4>
                      <div className="tools-list">
                        {message.tools_used.map((tool, index) => (
                          <span key={index} className="tool-badge">
                            {tool}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {message.isError && (
                  <div className="error-message">
                    ⚠️ {message.content}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message assistant">
              <div className="message-content">
                <div className="loading-indicator">
                  <div className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span>Agent is thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {conversationEnded && (
          <div className="conversation-ended">
            <p>💬 Conversation ended. Start a new conversation to continue.</p>
            <button className="reset-btn" onClick={resetConversation}>
              Start New Conversation
            </button>
          </div>
        )}

        <form onSubmit={handleSubmit} className="input-form">
          <div className="input-container">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={conversationEnded ? "Conversation ended. Start a new one." : "Type your message here..."}
              disabled={isLoading || conversationEnded}
              className="message-input"
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || isLoading || conversationEnded}
              className="send-button"
            >
              {isLoading ? '⏳' : '📤'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;
