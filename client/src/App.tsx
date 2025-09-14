import { ClientPage } from "@/components/ClientPage";
import ErrorPage from "@/components/ErrorPage";
import { Layout } from "@/components/Layout";
import QueryClientProvider from "@/components/QueryClientProvider";
import { Toaster } from "@/components/ui/toaster";
import { AppStateProvider } from "@/contexts/AppStateProvider";
import { LoaderCircleIcon } from "lucide-react";
import { useEffect, useState } from "react";

function App() {
  const [websocketEnabled, setWebsocketEnabled] = useState<boolean>();
  const [webrtcEnabled, setWebrtcEnabled] = useState<boolean>();

  useEffect(() => {
    const abort = new AbortController();
    const serverUrl = import.meta.env.VITE_SERVER_URL || 'http://127.0.0.1:7860/api';
    console.log('Fetching from:', serverUrl);
    fetch(`${serverUrl}/`, {
      signal: abort.signal,
    })
      .then((response) => {
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        console.log('Server response:', json);
        const wsEnabled = json?.["websocket-enabled"] ?? false;
        const webrtcEnabled = json?.["webrtc-enabled"] ?? false;
        console.log('Setting websocketEnabled to:', wsEnabled);
        console.log('Setting webrtcEnabled to:', webrtcEnabled);
        setWebsocketEnabled(wsEnabled);
        setWebrtcEnabled(webrtcEnabled);
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
