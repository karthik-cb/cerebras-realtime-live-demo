import { ClientPage } from "@/components/ClientPage";
import ErrorPage from "@/components/ErrorPage";
import { Layout } from "@/components/Layout";
import QueryClientProvider from "@/components/QueryClientProvider";
import { Toaster } from "@/components/ui/toaster";
import { AppStateProvider } from "@/contexts/AppStateProvider";
import { ModelOption } from "@/contexts/AppStateContext";
import { LoaderCircleIcon } from "lucide-react";
import { useEffect, useState } from "react";

function App() {
  const [websocketEnabled, setWebsocketEnabled] = useState<boolean>();
  const [webrtcEnabled, setWebrtcEnabled] = useState<boolean>();
  const [availableModels, setAvailableModels] = useState<{
    stt: ModelOption[];
    llm: ModelOption[];
    tts: ModelOption[];
    mcp: ModelOption[];
  }>({
    stt: [],
    llm: [],
    tts: [],
    mcp: [],
  });

  useEffect(() => {
    const abort = new AbortController();
    console.log('VITE_SERVER_URL from env:', import.meta.env.VITE_SERVER_URL);
    console.log('All env vars:', import.meta.env);
    const serverUrl = import.meta.env.VITE_SERVER_URL || 'http://127.0.0.1:7860/api';
    console.log('Final serverUrl:', serverUrl);
    console.log('Fetching from:', serverUrl);
    
    // Fetch both config and models
    Promise.all([
      fetch(`${serverUrl}/`, { signal: abort.signal }),
      fetch(`${serverUrl}/models`, { signal: abort.signal })
    ])
      .then(([configResponse, modelsResponse]) => {
        console.log('Config response status:', configResponse.status);
        console.log('Models response status:', modelsResponse.status);
        
        if (!configResponse.ok) {
          throw new Error(`HTTP error! status: ${configResponse.status}`);
        }
        if (!modelsResponse.ok) {
          throw new Error(`HTTP error! status: ${modelsResponse.status}`);
        }
        
        return Promise.all([configResponse.json(), modelsResponse.json()]);
      })
      .then(([configJson, modelsJson]) => {
        console.log('Server config:', configJson);
        console.log('Available models:', modelsJson);
        
        const wsEnabled = configJson?.["websocket-enabled"] ?? false;
        const webrtcEnabled = configJson?.["webrtc-enabled"] ?? false;
        console.log('Setting websocketEnabled to:', wsEnabled);
        console.log('Setting webrtcEnabled to:', webrtcEnabled);
        setWebsocketEnabled(wsEnabled);
        setWebrtcEnabled(webrtcEnabled);
        
        // Set available models
        if (modelsJson?.models) {
          setAvailableModels(modelsJson.models);
        }
      })
      .catch((error) => {
        console.error('Error fetching server config:', error);
        setWebsocketEnabled(false);
        setWebrtcEnabled(false);
      });
    return () => abort.abort();
  }, []);

  console.log('App render - websocketEnabled:', websocketEnabled, 'webrtcEnabled:', webrtcEnabled);

  if (websocketEnabled === undefined && webrtcEnabled === undefined) {
    return (
      <Layout>
        <div className="h-full flex items-center justify-center">
          <LoaderCircleIcon className="animate-spin" />
        </div>
      </Layout>
    );
  }

  if (!websocketEnabled && !webrtcEnabled) {
    return (
      <ErrorPage title="Missing configuration">
        The server is missing required API keys for the TTS-LLM-STT pipeline. 
        Please ensure <code>DEEPGRAM_API_KEY</code> and <code>CEREBRAS_API_KEY</code> are set.
        For WebRTC features, <code>DAILY_API_KEY</code> is also required.
      </ErrorPage>
    );
  }

  return (
    <QueryClientProvider>
      <AppStateProvider
        webrtcEnabled={webrtcEnabled ?? false}
        websocketEnabled={websocketEnabled ?? false}
        availableModels={availableModels}
      >
        <Layout>
          <ClientPage />
          <Toaster />
        </Layout>
      </AppStateProvider>
    </QueryClientProvider>
  );
}

export default App;
