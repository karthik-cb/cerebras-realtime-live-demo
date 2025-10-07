import React from "react";
import { ExternalLinkIcon, CreditCardIcon, ShipIcon } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface MCPTool {
  name: string;
  description: string;
  icon: React.ReactNode;
  capabilities: string[];
  documentationUrl: string;
  requiresAuth: boolean;
  status: "available" | "requires_setup";
}

const mcpTools: MCPTool[] = [
  {
    name: "PayPal Business Tools",
    description: "Create invoices, manage payments, and handle subscriptions through natural language",
    icon: <CreditCardIcon className="h-5 w-5" />,
    capabilities: [
      "Create and send invoices",
      "Process payments and refunds", 
      "Manage subscriptions",
      "Handle customer data",
      "Generate business reports"
    ],
    documentationUrl: "https://docs.paypal.ai/developer/tools/ai/mcp-quickstart",
    requiresAuth: true,
    status: "requires_setup"
  },
  {
    name: "Ferryhopper Travel Planning",
    description: "Search ferry routes, schedules, and get booking links across Europe and the Mediterranean",
    icon: <ShipIcon className="h-5 w-5" />,
    capabilities: [
      "Search ferry routes and schedules",
      "Get real-time pricing information",
      "Find ports across 33 countries",
      "Plan island-hopping journeys",
      "Get direct booking links"
    ],
    documentationUrl: "https://ferryhopper.github.io/fh-mcp/",
    requiresAuth: false,
    status: "available"
  }
];

export function MCPToolsOverview() {
  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h3 className="text-lg font-semibold text-neutral-700 mb-2">
          Available AI Tools & Capabilities
        </h3>
        <p className="text-sm text-neutral-500">
          This voice assistant integrates with powerful external tools through Model Context Protocol (MCP)
        </p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-3xl mx-auto">
        {mcpTools.map((tool) => (
          <Card key={tool.name} className="relative">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
                  {tool.icon}
                </div>
                <div className="flex-1">
                  <CardTitle className="text-base flex items-center gap-2">
                    {tool.name}
                    <Badge 
                      variant={tool.status === "available" ? "default" : "secondary"}
                      className="text-xs"
                    >
                      {tool.status === "available" ? "Ready" : "Setup Required"}
                    </Badge>
                  </CardTitle>
                </div>
              </div>
              <CardDescription className="text-sm">
                {tool.description}
              </CardDescription>
            </CardHeader>
            
            <CardContent className="pt-0">
              <div className="space-y-3">
                <div>
                  <h4 className="text-xs font-medium text-neutral-600 mb-2">Capabilities:</h4>
                  <ul className="text-xs text-neutral-500 space-y-1">
                    {tool.capabilities.map((capability, index) => (
                      <li key={index} className="flex items-center gap-2">
                        <div className="w-1 h-1 bg-neutral-400 rounded-full" />
                        {capability}
                      </li>
                    ))}
                  </ul>
                </div>
                
                {tool.requiresAuth && (
                  <div className="p-2 bg-amber-50 border border-amber-200 rounded-md">
                    <p className="text-xs text-amber-700">
                      <strong>Setup Required:</strong> Enable in settings tab on the top right of the screen.
                    </p>
                  </div>
                )}
                
                <div className="flex items-center gap-2 pt-2">
                  <a
                    href={tool.documentationUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 transition-colors"
                  >
                    <ExternalLinkIcon className="h-3 w-3" />
                    Documentation
                  </a>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-3">
          <div className="p-1 bg-blue-100 rounded">
            <ExternalLinkIcon className="h-4 w-4 text-blue-600" />
          </div>
          <div>
            <h4 className="text-sm font-medium text-blue-900 mb-1">
              How to Enable Additional Tools
            </h4>
            <p className="text-xs text-blue-700 mb-2">
              Some tools require additional setup. Click the settings icon in the top-right corner to configure:
            </p>
            <ul className="text-xs text-blue-700 space-y-1">
              <li>• <strong>PayPal:</strong> Enable sandbox mode and configure API credentials</li>
              <li>• <strong>Ferryhopper:</strong> Ready to use - no setup required</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
