import React, { useState } from "react";
import { MessageSquareIcon, CreditCardIcon, ShipIcon } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface ExamplePrompt {
  category: string;
  icon: React.ReactNode;
  prompts: string[];
  color: string;
}

const examplePrompts: ExamplePrompt[] = [
  {
    category: "Ferry Travel Planning",
    icon: <ShipIcon className="h-4 w-4" />,
    color: "bg-blue-50 border-blue-200 text-blue-700",
    prompts: [
      "What ferries go from Athens to Santorini tomorrow?",
      "Find ferries from Barcelona to Ibiza on July 15th",
      "Plan a multi-island trip from Athens to Mykonos, then Santorini",
      "Show me ferry ports in the Greek islands",
      "I want to visit an island within 3 hours of Athens tomorrow"
    ]
  },
  {
    category: "PayPal Business",
    icon: <CreditCardIcon className="h-4 w-4" />,
    color: "bg-green-50 border-green-200 text-green-700",
    prompts: [
      "Create an invoice for landscaping services for $200",
      "Send an invoice to john@example.com for $150",
      "List my PayPal invoices from last month",
      "Check the status of invoice INV-12345",
      "Create a subscription for monthly software license"
    ]
  }
];

export function ExamplePrompts() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="text-center mb-6">
        <h3 className="text-lg font-semibold text-neutral-700 mb-2">
          Try These Example Prompts
        </h3>
        <p className="text-sm text-neutral-500">
          Click on any category to see example voice commands you can try
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
        {examplePrompts.map((category) => (
          <Card 
            key={category.category}
            className={`cursor-pointer transition-all hover:shadow-md ${
              selectedCategory === category.category 
                ? 'ring-2 ring-blue-500 shadow-md' 
                : 'hover:shadow-sm'
            }`}
            onClick={() => setSelectedCategory(
              selectedCategory === category.category ? null : category.category
            )}
          >
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <div className={`p-1.5 rounded-md ${category.color}`}>
                  {category.icon}
                </div>
                <CardTitle className="text-sm font-medium">
                  {category.category}
                </CardTitle>
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>
      
      {selectedCategory && (
        <Card className="mt-4 border-blue-200 bg-blue-50/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              {examplePrompts.find(cat => cat.category === selectedCategory)?.icon}
              {selectedCategory} Examples
            </CardTitle>
            <CardDescription>
              Try saying these phrases to test the voice assistant capabilities
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="space-y-2">
              {examplePrompts
                .find(cat => cat.category === selectedCategory)
                ?.prompts.map((prompt, index) => (
                  <div 
                    key={index}
                    className="p-3 bg-white border border-blue-200 rounded-lg text-sm"
                  >
                    <div className="flex items-start gap-2">
                      <MessageSquareIcon className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                      <span className="text-neutral-700">"{prompt}"</span>
                    </div>
                  </div>
                ))}
            </div>
            <div className="mt-3 p-2 bg-blue-100 border border-blue-200 rounded-md">
              <p className="text-xs text-blue-700">
                <strong>Tip:</strong> Click the microphone button above to start a voice conversation, then try saying one of these prompts!
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
