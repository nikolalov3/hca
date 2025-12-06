import React, { useState, useEffect } from 'react';
import { User, Calendar, MapPin, Clock, PlusCircle, Camera, Lock } from 'lucide-react';
import { TonConnectButton, useTonWallet } from '@tonconnect/ui-react';
import axios from 'axios';

// --- KOMPONENTY UI ---

const MatchCard = ({ match, onJoin, isWalletConnected }) => (
  <div className="bg-white dark:bg-cardDark rounded-2xl p-5 mb-4 shadow-sm border-2 border-babyBlue/30 hover:border-babyBlue transition-all duration-300">
    <div className="flex justify-between items-start mb-3">
      <div>
        <h3 className="font-bold text-xl text-gray-800 dark:text-white">{match.venue}</h3>
        <div className="flex items-center text-gray-500 dark:text-gray-400 text-sm mt-1">
          <MapPin size={14} className="mr-1 text-babyBlue" />
          <span>Warszawa, Mokotów</span>
        </div>
      </div>
      <div className="bg-babyBlue/10 dark:bg-babyOrange/10 text-babyBlue dark:text-babyOrange font-bold px-3 py-1 rounded-lg text-sm border border-babyBlue/20 dark:border-babyOrange/20">
        {match.price}
      </div>
    </div>

    <div className="flex items-center gap-4 my-4">
      <div className="flex items-center text-gray-600 dark:text-gray-300 text-sm font-medium">
        <Calendar size={18} className="mr-2 text-babyGreen dark:text-babyOrange" />
        {match.date}
      </div>
    </div>

    {/* Pasek postępu */}
    <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-3 mb-4 overflow-hidden">
      <div 
        className="bg-babyGreen dark:bg-babyOrange h-3 rounded-full transition-all duration-500" 
        style={{ width: `${(parseInt(match.slots) / 10) * 100}%` }}
      ></div>
    </div>
    
    <div className="flex justify-between items-center mt-2">
      <span className="text-sm text-gray-500 dark:text-gray-400 font-medium">
        Gracze: <span className="text-gray-800 dark:text-white">{match.slots}</span>
      </span>

      {/* Logika przycisku Dołącz */}
      {match.status === 'full' ? (
         <button disabled className="px-5 py-2.5 rounded-xl font-bold text-sm bg-gray-100 text-gray-400 border border-gray-200 cursor-not-allowed">
            Pełny skład
         </button>
      ) : !isWalletConnected ? (
        <button 
            onClick={() => alert("Musisz połączyć portfel, aby grać! 🏀")}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm bg-gray-100 text-gray-500 border-2 border-gray-200 hover:bg-gray-200 transition-colors"
        >
            <Lock size={14} />
            Dołącz
        </button>
      ) : (
        <button 
            onClick={() => onJoin(match.id)}
            className="px-5 py-2.5 rounded-xl font-bold text-sm bg-black text-white dark:bg-babyOrange dark:text-black shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 border-2 border-transparent"
        >
            Dołącz do gry
        </button>
      )}
    </div>
  </div>
);

const ProfileView = () => (
  <div className="p-4">
    <div className="flex flex-col items-center mb-8">
      <div className="w-28 h-28 bg-gray-100 dark:bg-gray-800 rounded-full mb-4 relative border-4 border-white shadow-lg">
        <div className="absolute bottom-0 right-0 bg-babyBlue dark:bg-babyOrange p-2.5 rounded-full text-white dark:text-black shadow-md cursor-pointer hover:scale-110 transition-transform">
          <Camera size={18} />
        </div>
      </div>
      <h2 className="text-2xl font-bold dark:text-white">Twój Profil</h2>
      <p className="text-gray-400 text-sm">Uzupełnij dane, by grać</p>
    </div>

    <div className="space-y-5">
      {['Imię', 'Wiek', 'Wzrost (cm)', 'Numer na koszulce'].map((label) => (
        <div key={label}>
          <label className="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-2 ml-1">
            {label}
          </label>
          <input 
            type="text" 
            className="w-full p-4 rounded-2xl bg-white dark:bg-cardDark border-2 border-gray-100 dark:border-gray-700 text-gray-800 dark:text-white focus:border-babyBlue dark:focus:border-babyOrange outline-none transition-all font-medium"
            placeholder="..."
          />
        </div>
      ))}
    </div>

    <button className="w-full mt-8 bg-babyBlue text-white font-bold py-4 rounded-2xl shadow-lg shadow-blue-200 dark:shadow-none hover:brightness-105 transition-all">
        Zapisz Zmiany
    </button>
  </div>
);

// --- GŁÓWNA APLIKACJA ---

function App() {
  const [activeTab, setActiveTab] = useState('play');
  const wallet = useTonWallet(); // Hook sprawdzający czy portfel jest podpięty
  const [matches, setMatches] = useState([
    { id: 1, venue: "Arena Ursynów", date: "Dziś, 18:00", price: "15 PLN", slots: "4/10", status: "open" },
    { id: 2, venue: "OSiR Wola", date: "Jutro, 20:00", price: "20 PLN", slots: "10/10", status: "full" }
  ]);

  return (
    <div className="min-h-screen bg-white dark:bg-bgDark pb-24 font-sans selection:bg-babyBlue selection:text-white">
      {/* HEADER */}
      <header className="sticky top-0 z-20 bg-white/90 dark:bg-bgDark/90 backdrop-blur-md px-5 py-4 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center">
        <div className="flex items-center gap-0.5 select-none">
            <span className="text-2xl font-black text-babyBlue tracking-tighter">HOOP.</span>
            <span className="text-2xl font-black text-babyGreen tracking-tighter">CONNECT</span>
        </div>
        
        {/* Przycisk TON Connect (skalowalny) */}
        <div className="transform scale-90 origin-right">
            <TonConnectButton />
        </div>
      </header>

      <main className="p-5 max-w-md mx-auto">
        {activeTab === 'play' ? (
          <>
            {/* ALERT POWITALNY (BEZ GRADIENTU) */}
            <div className={`mb-6 p-5 rounded-2xl border-2 ${wallet ? 'bg-babyGreen/10 border-babyGreen/30' : 'bg-babyBlue/5 border-babyBlue/20'}`}>
              <div className="flex items-center gap-3 mb-1">
                <span className="text-2xl">🏀</span>
                <h2 className={`font-bold text-lg ${wallet ? 'text-green-700 dark:text-green-400' : 'text-gray-800 dark:text-white'}`}>
                    {wallet ? 'Gotowy do gry!' : 'Witaj na boisku!'}
                </h2>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed ml-10">
                {wallet 
                    ? `Twój portfel jest podłączony: ${wallet.account.address.slice(0,4)}...${wallet.account.address.slice(-4)}`
                    : 'Zaloguj się portfelem (prawy górny róg), aby dołączyć do meczu.'}
              </p>
            </div>

            <div className="space-y-2">
              {matches.map(match => (
                <MatchCard 
                    key={match.id} 
                    match={match} 
                    isWalletConnected={!!wallet}
                    onJoin={(id) => alert(`Dołączasz do meczu ${id}!`)} 
                />
              ))}
            </div>
          </>
        ) : (
          <ProfileView />
        )}
      </main>

      {/* BOTTOM NAVIGATION */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white dark:bg-cardDark border-t border-gray-100 dark:border-gray-800 px-8 py-4 flex justify-between items-center z-30 pb-safe shadow-[0_-5px_20px_rgba(0,0,0,0.03)]">
        <button 
          onClick={() => setActiveTab('play')}
          className={`flex flex-col items-center gap-1 transition-colors ${activeTab === 'play' ? 'text-babyBlue' : 'text-gray-300 hover:text-gray-400'}`}
        >
          <Calendar size={26} strokeWidth={activeTab === 'play' ? 2.5 : 2} />
        </button>

        <button 
          className="bg-black dark:bg-babyOrange text-white dark:text-black p-4 rounded-full -mt-12 shadow-xl border-[6px] border-white dark:border-bgDark transform active:scale-95 transition-transform hover:shadow-2xl hover:-translate-y-1"
        >
          <PlusCircle size={32} />
        </button>

        <button 
          onClick={() => setActiveTab('profile')}
          className={`flex flex-col items-center gap-1 transition-colors ${activeTab === 'profile' ? 'text-babyBlue' : 'text-gray-300 hover:text-gray-400'}`}
        >
           <User size={26} strokeWidth={activeTab === 'profile' ? 2.5 : 2} />
        </button>
      </nav>
    </div>
  );
}

export default App;
