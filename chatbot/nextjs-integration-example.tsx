// Example Next.js integration for Finance LLM Chatbot
// File: components/FinanceChatbot.tsx

import { useState } from "react";

// Types for API requests and responses
interface ChatRequest {
  message: string;
  api_key?: string;
  model_name?: string;
}

interface ChatResponse {
  response: string;
  status: string;
  message_type: string;
}

interface StockPriceRequest {
  ticker: string;
}

interface StockPriceResponse {
  ticker: string;
  company_name: string;
  current_price: number;
  currency: string;
  change_percent?: number;
  status: string;
}

interface ImageResponse {
  filename: string;
  url: string;
  type: string;
  description?: string;
}

interface ImagesListResponse {
  images: ImageResponse[];
  count: number;
  message: string;
}

const API_BASE_URL = "http://localhost:8001";
const IMAGE_SERVER_URL = "http://localhost:8002";

export default function FinanceChatbot() {
  const [messages, setMessages] = useState<
    Array<{ text: string; isUser: boolean; imageUrl?: string }>
  >([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [availableImages, setAvailableImages] = useState<ImageResponse[]>([]);
  const [showImageGallery, setShowImageGallery] = useState(false);

  // General chat function
  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = inputMessage;
    setInputMessage("");
    setIsLoading(true);

    // Add user message to chat
    setMessages((prev) => [...prev, { text: userMessage, isUser: true }]);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
          api_key: apiKey || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: ChatResponse = await response.json();

      // Check for latest image if it's a visual analysis type
      const imageUrl = await checkForLatestImage(data.message_type);

      // Add bot response to chat
      setMessages((prev) => [
        ...prev,
        {
          text: data.response,
          isUser: false,
          imageUrl: imageUrl || undefined,
        },
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        {
          text: "Sorry, I encountered an error. Please try again.",
          isUser: false,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Get specific stock price
  const getStockPrice = async (ticker: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/stock/price`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ticker }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: StockPriceResponse = await response.json();

      const priceMessage =
        `${data.company_name} (${data.ticker}) is currently trading at ${
          data.currency
        }${data.current_price.toFixed(2)}` +
        (data.change_percent
          ? `, ${
              data.change_percent > 0 ? "+" : ""
            }${data.change_percent.toFixed(2)}% from previous close.`
          : ".");

      setMessages((prev) => [
        ...prev,
        {
          text: priceMessage,
          isUser: false,
        },
      ]);
    } catch (error) {
      console.error("Error getting stock price:", error);
      setMessages((prev) => [
        ...prev,
        {
          text: `Sorry, I couldn't retrieve the price for ${ticker}.`,
          isUser: false,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Check API health
  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      const data = await response.json();
      console.log("API Health:", data);
      return data.status === "healthy";
    } catch (error) {
      console.error("API health check failed:", error);
      return false;
    }
  };

  // Image handling functions
  const fetchLatestImages = async () => {
    try {
      const response = await fetch(`${IMAGE_SERVER_URL}/images`);
      if (response.ok) {
        const data: ImagesListResponse = await response.json();
        setAvailableImages(data.images);
      }
    } catch (error) {
      console.error("Error fetching images:", error);
    }
  };

  const checkForLatestImage = async (messageType: string) => {
    try {
      let imageType = "";
      if (messageType === "stock_comparison") imageType = "comparison";
      else if (messageType === "performance_analysis")
        imageType = "performance";
      else if (messageType === "stock_analysis") imageType = "stock_analysis";

      if (imageType) {
        const response = await fetch(`${IMAGE_SERVER_URL}/images/latest`);
        if (response.ok) {
          const data = await response.json();
          return data.url;
        }
      }
    } catch (error) {
      console.error("Error checking for latest image:", error);
    }
    return null;
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        Finance LLM Chatbot
      </h1>

      {/* API Key Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Hugging Face API Key (Optional)
        </label>
        <input
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder="hf_..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Image Gallery Toggle */}
      <div className="mb-4 flex gap-2">
        <button
          onClick={fetchLatestImages}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Refresh Images
        </button>
        <button
          onClick={() => setShowImageGallery(!showImageGallery)}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          {showImageGallery ? "Hide" : "Show"} Plot Gallery (
          {availableImages.length})
        </button>
      </div>

      {/* Image Gallery */}
      {showImageGallery && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold mb-3">Generated Stock Plots</h3>
          {availableImages.length === 0 ? (
            <p className="text-gray-500">
              No plots available. Ask questions about stock analysis,
              comparisons, or performance to generate plots!
            </p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {availableImages.map((image, index) => (
                <div key={index} className="border rounded-lg p-2 bg-white">
                  <img
                    src={image.url}
                    alt={image.description || image.filename}
                    className="w-full h-48 object-contain rounded"
                  />
                  <p className="text-sm text-gray-600 mt-2">
                    {image.description || image.filename}
                  </p>
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {image.type}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Chat Messages */}
      <div className="h-96 overflow-y-auto mb-4 p-4 border border-gray-300 rounded-md bg-gray-50">
        {messages.length === 0 && (
          <div className="text-gray-500 text-center">
            Start a conversation! Try asking about stocks, financial concepts,
            or market analysis.
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`mb-3 p-3 rounded-lg ${
              message.isUser
                ? "bg-blue-500 text-white ml-auto max-w-xs"
                : "bg-white text-gray-800 mr-auto max-w-2xl"
            }`}
          >
            <div className="whitespace-pre-wrap">{message.text}</div>
            {/* Display image if available */}
            {message.imageUrl && (
              <img
                src={message.imageUrl}
                alt="Generated visual content"
                className="mt-2 max-w-full h-auto rounded-md"
              />
            )}
          </div>
        ))}

        {isLoading && (
          <div className="bg-white text-gray-800 mr-auto max-w-2xl mb-3 p-3 rounded-lg">
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900 mr-2"></div>
              Thinking...
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Ask about stocks, financial concepts, or market analysis..."
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        />
        <button
          onClick={sendMessage}
          disabled={isLoading || !inputMessage.trim()}
          className="px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </div>

      {/* Quick Action Buttons */}
      <div className="flex flex-wrap gap-2 mb-4">
        <button
          onClick={() => getStockPrice("AAPL")}
          disabled={isLoading}
          className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:bg-gray-400"
        >
          Apple Stock Price
        </button>
        <button
          onClick={() => getStockPrice("GOOGL")}
          disabled={isLoading}
          className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:bg-gray-400"
        >
          Google Stock Price
        </button>
        <button
          onClick={() => setInputMessage("What is diversification?")}
          disabled={isLoading}
          className="px-4 py-2 bg-purple-500 text-white rounded-md hover:bg-purple-600 disabled:bg-gray-400"
        >
          Ask about Diversification
        </button>
        <button
          onClick={() => setInputMessage("Should I buy Tesla stock?")}
          disabled={isLoading}
          className="px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600 disabled:bg-gray-400"
        >
          Investment Advice
        </button>
      </div>

      {/* API Status */}
      <div className="text-sm text-gray-600">
        <button
          onClick={checkApiHealth}
          className="text-blue-500 hover:text-blue-700 underline"
        >
          Check API Status
        </button>
      </div>
    </div>
  );
}
