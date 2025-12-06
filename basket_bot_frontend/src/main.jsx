import React from 'react'
import ReactDOM from 'react-dom/client'
import { TonConnectUIProvider } from '@tonconnect/ui-react';
import App from './App.jsx'
import './index.css'

// Twój adres z ngroka + ścieżka do pliku, który stworzyłeś wyżej
const manifestUrl = 'https://raw.githubusercontent.com/nikolalov3/hca/refs/heads/main/basket_bot_backend/public/tonconnect-manifest.json';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <TonConnectUIProvider manifestUrl={manifestUrl}>
      <App />
    </TonConnectUIProvider>
  </React.StrictMode>,
)
