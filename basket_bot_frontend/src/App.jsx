import React, { useState, useEffect } from 'react';
import { User, Calendar, MapPin, PlusCircle, Camera, Lock, Trophy, Activity } from 'lucide-react';
import { TonConnectButton, useTonWallet } from '@tonconnect/ui-react';
import axios from 'axios';

// --- KONFIGURACJA ---
// Tutaj wkleimy adres Twojego Backendu z Railway, jak już wstanie.
// Na razie zostawiam localhost do testów lub pusty string.
const API_URL = "https://hca-production.up.railway.app"; 

// --- KOMPONENTY UI ---

const Header = () => (
  <header className="sticky top-0 z-30 bg-white/80 dark:bg-[#1A1A1A]/80 backdrop-blur-xl border-b border-gray-100 dark:border-white/10 px-6 py-4 flex justify-between items-center transition-colors duration-300">
    <div className="flex items-center gap-1 select-none">
      {/* Logo tekstowe */}
      <span className="text-2xl font-black text-babyBlue dark:text-white tracking-tighter">HOOP.</span>
      <span className="text-2xl font-black text-babyGreen dark:text-babyOrange tracking-tighter">CONNECT</span>
    </div>
    
    {/* Przycisk Wallet - Skalowalny */}
    <div className="transform scale-90 origin-right">
       <TonConnectButton />
    </div>
  </header>
);

const MatchCard = ({ match, onJoin, isWalletConnected }) => {
  const isFull = match.slots.split('/')[0] === match.slots.split('/')[1];

  return (
    <div className="group relative bg-white dark:bg-[#2C2C2C] rounded-3xl p-6 mb-5 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-none border border-gray-100 dark:border-white/5 hover:border-babyBlue dark:hover:border-babyOrange transition-all duration-300">
      
      {/* Status Badge */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-bold text-xl text-gray-900 dark:text-white tracking-tight">{match.venue}</h3>
          <div className="flex items-center text-gray-400 dark:text-gray-400 text-sm mt-1.5 font-medium">
            <MapPin size={14} className="mr-1.5 text-babyBlue dark:text-babyOrange" />
            <span>Warszawa, Mokotów</span>
          </div>
        </div>
        <div className="bg-babyBlue/10 dark:bg-babyOrange/10 text-babyBlue dark:text-babyOrange font-bold px-4 py-1.5 rounded-full text-sm border border-babyBlue/20 dark:border-babyOrange/20 backdrop-blur-sm">
          {match.price}
        </div>
      </div>

      {/* Info Grid */}
      <div className="flex items-center gap-6 my-5">
        <div className="flex items-center text-gray-600 dark:text-gray-300 text-sm font-semibold">
          <div className="p-2 rounded-lg bg-gray-50 dark:bg-white/5 mr-3">
             <Calendar size={18} className="text-gray-900 dark:text-white" />
          </div>
          {match.date}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="relative w-full bg-gray-100 dark:bg-white/10 rounded-full h-2.5 mb-5 overflow-hidden">
        <div 
          className="absolute top-0 left-0 h-full bg-gradient-to-r from-babyBlue to-babyGreen dark:from-orange-400 dark:to-babyOrange rounded-full transition-all duration-700 ease-out" 
          style={{ width: `${(parseInt(match.slots) / 10) * 100}%` }}
        ></div>
      </div>
      
      {/* Footer & Action */}
      <div className="flex justify-between items-center mt-2">
        <span className="text-sm text-gray-500 dark:text-gray-400 font-medium">
          Gracze: <span className="text-gray-900 dark:text-white font-bold ml-1">{match.slots}</span>
        </span>

        {isFull ? (
           <button disabled className="px-6 py-3 rounded-2xl font-bold text-sm bg-gray-100 dark:bg-white/5 text-gray-400 border border-transparent cursor-not-allowed">
              Pełny skład
           </button>
        ) : !isWalletConnected ? (
          <button 
              onClick={() => alert("Musisz połączyć portfel, aby grać! 🏀")}
              className="flex items-center gap-2 px-6 py-3 rounded-2xl font-bold text-sm bg-gray-50 dark:bg-white/5 text-gray-500 dark:text-gray-300 border border-gray-200 dark:border-white/10 hover:bg-gray-100 dark:hover:bg-white/10 transition-colors"
          >
              <Lock size={16} />
              Dołącz
          </button>
        ) : (
          <button 
              onClick={() => onJoin(match.id)}
              className="px-6 py-3 rounded-2xl font-bold text-sm bg-gray-900 text-white dark:bg-babyOrange dark:text-black shadow-lg shadow-babyBlue/20 dark:shadow-babyOrange/20 hover:scale-105 active:scale-95 transition-all duration-300"
          >
              Dołącz do gry
          </button>
        )}
      </div>
    </div>
  );
};

const ProfileView = () => {
  const [profile, setProfile] = useState(null);
  const [formData, setFormData] = useState({ nickname: '', age: '', city: '', skill_level: '', preferred_position: '', bio: '', phone: '' });
  const [status, setStatus] = useState('');
  const wallet = useTonWallet();
  
  useEffect(() => {
    if (!wallet) return;
    const fetchProfile = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/profile/me`, {
          headers: { 'Authorization': `Bearer ${wallet.account.address}` }
        });
        if (response.data.profile) {
          setProfile(response.data.profile);
          setFormData(response.data.profile);
        }
      } catch (e) { console.error(e); }
    };
    fetchProfile();
  }, [wallet]);
  
  const handleChange = (e) => setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  
  const handleSave = async () => {
    setStatus('saving');
    try {
      const response = await axios.post(`${API_URL}/api/profile/me`, formData, {
        headers: { 'Authorization': `Bearer ${wallet.account.address}` }
      });
      if (response.data.status === 'success') {
        setProfile(response.data.profile);
        setStatus('saved');
        setTimeout(() => setStatus(''), 3000);
      }
    } catch (e) { setStatus('error'); }
  };
  
  return (
    <div className="p-6 pb-32">
      <div className="flex flex-col items-center mb-10">
        <div className="w-32 h-32 bg-gray-50 dark:bg-[#2C2C2C] rounded-full mb-6 relative border-4 border-white dark:border-[#2C2C2C] shadow-xl flex items-center justify-center overflow-hidden">
          <User size={48} className="text-gray-300 dark:text-white/20" />
          <div className="absolute bottom-1 right-1 bg-babyBlue dark:bg-babyOrange p-3 rounded-full text-white dark:text-black shadow-lg cursor-pointer hover:scale-110 transition-transform">
            <Camera size={18} strokeWidth={2.5} />
          </div>
        </div>
        <h2 className="text-3xl font-black text-gray-900 dark:text-white tracking-tight">Twój Profil</h2>
        <p className="text-gray-400 text-base mt-1 font-medium">Uzupełnij dane gracza</p>
      </div>
      <div className="space-y-6">
        {[
          { l: 'Nick gracza', k: 'nickname' },
          { l: 'Wiek', k: 'age', n: true },
          { l: 'Miasto', k: 'city' },
          { l: 'Poziom (beginner/intermediate/advanced)', k: 'skill_level' },
          { l: 'Pozycja (G/F/C)', k: 'preferred_position' },
          { l: 'Bio', k: 'bio' },
          { l: 'Numer telefonu', k: 'phone' }
        ].map((field) => (
          <div key={field.k}>
            <label className="block text-xs font-bold uppercase tracking-widest text-gray-400 dark:text-gray-500 mb-2.5 ml-1">
              {field.l}
            </label>
            <input
              name={field.k}
              value={formData[field.k] || ''}
              onChange={handleChange}
              type={field.n ? 'number' : 'text'}
              className="w-full p-4 rounded-2xl bg-gray-50 dark:bg-[#2C2C2C] border-2 border-transparent focus:bg-white dark:focus:bg-[#2C2C2C] focus:border-babyBlue dark:focus:border-babyOrange text-gray-900 dark:text-white placeholder-gray-300 dark:placeholder-gray-600 outline-none transition-all font-semibold text-lg"
              placeholder="..."
            />
          </div>
        ))}
      </div>
      <button
        onClick={handleSave}
        disabled={status === 'saving'}
        className={`w-full mt-10 font-bold py-4.5 rounded-2xl shadow-xl transition-all duration-300 text-lg ${
          status === 'saved' ? 'bg-green-500 text-white shadow-green-500/20' :
          status === 'error' ? 'bg-red-500 text-white shadow-red-500/20' :
          'bg-babyBlue text-white dark:bg-babyOrange dark:text-black shadow-babyBlue/30 dark:shadow-babyOrange/20 hover:-translate-y-1'
        }`}
      >
        {status === 'saving' ? 'Zapisywanie...' :
         status === 'saved' ? 'Zapisano ✓' :
         status === 'error' ? 'Błąd (Sprawdź sieć)' : 'Zapisz Profil'}
      </button>
    </div>
  );
}
130
  96
    99
      96
        = ({ telegramId }) => {
  const [formData, setFormData] = useState({ name: '', age: '', height: '', number: '', wallet_address: '' });
  const [status, setStatus] = useState('');
  const wallet = useTonWallet();

  useEffect(() => {
    if (!telegramId) return;
    const fetchData = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/profile/${telegramId}`);
        if (response.data) setFormData(prev => ({ ...prev, ...response.data }));
      } catch (e) { console.error(e); }
    };
    fetchData();
  }, [telegramId]);

  useEffect(() => {
    if (wallet) setFormData(prev => ({ ...prev, wallet_address: wallet.account.address }));
  }, [wallet]);

  const handleChange = (e) => setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSave = async () => {
    setStatus('saving');
    try {
      await axios.post(`${API_URL}/api/profile`, { telegram_id: telegramId, ...formData });
      setStatus('saved');
      setTimeout(() => setStatus(''), 3000);
    } catch (e) { setStatus('error'); }
  };

  return (
    <div className="p-6 pb-32">
      <div className="flex flex-col items-center mb-10">
        <div className="w-32 h-32 bg-gray-50 dark:bg-[#2C2C2C] rounded-full mb-6 relative border-4 border-white dark:border-[#2C2C2C] shadow-xl flex items-center justify-center overflow-hidden">
             <User size={48} className="text-gray-300 dark:text-white/20" />
             <div className="absolute bottom-1 right-1 bg-babyBlue dark:bg-babyOrange p-3 rounded-full text-white dark:text-black shadow-lg cursor-pointer hover:scale-110 transition-transform">
              <Camera size={18} strokeWidth={2.5} />
            </div>
        </div>
        <h2 className="text-3xl font-black text-gray-900 dark:text-white tracking-tight">Twój Profil</h2>
        <p className="text-gray-400 text-base mt-1 font-medium">Uzupełnij statystyki gracza</p>
      </div>

      <div className="space-y-6">
        {[{l:'Imię / Nick', k:'name'}, {l:'Wiek', k:'age', n:true}, {l:'Wzrost (cm)', k:'height', n:true}, {l:'Numer', k:'number', n:true}].map((field) => (
          <div key={field.k}>
            <label className="block text-xs font-bold uppercase tracking-widest text-gray-400 dark:text-gray-500 mb-2.5 ml-1">
              {field.l}
            </label>
            <input 
              name={field.k}
              value={formData[field.k]}
              onChange={handleChange}
              type={field.n ? 'number' : 'text'}
              className="w-full p-4 rounded-2xl bg-gray-50 dark:bg-[#2C2C2C] border-2 border-transparent focus:bg-white dark:focus:bg-[#2C2C2C] focus:border-babyBlue dark:focus:border-babyOrange text-gray-900 dark:text-white placeholder-gray-300 dark:placeholder-gray-600 outline-none transition-all font-semibold text-lg"
              placeholder="..."
            />
          </div>
        ))}
      </div>

      <button 
        onClick={handleSave}
        disabled={status === 'saving'}
        className={`w-full mt-10 font-bold py-4.5 rounded-2xl shadow-xl transition-all duration-300 text-lg ${
            status === 'saved' ? 'bg-green-500 text-white shadow-green-500/20' : 
            status === 'error' ? 'bg-red-500 text-white shadow-red-500/20' :
            'bg-babyBlue text-white dark:bg-babyOrange dark:text-black shadow-babyBlue/30 dark:shadow-babyOrange/20 hover:-translate-y-1'
        }`}
      >
          {status === 'saving' ? 'Zapisywanie...' : 
           status === 'saved' ? 'Zapisano ✓' : 
           status === 'error' ? 'Błąd (Sprawdź sieć)' : 'Zapisz Statystyki'}
      </button>
    </div>
  );
};

// --- GŁÓWNA APLIKACJA ---

function App() {
  const [activeTab, setActiveTab] = useState('play');
  const wallet = useTonWallet();
  const [matches] = useState([
    { id: 1, venue: "Arena Ursynów", date: "Dziś, 18:00", price: "15 PLN", slots: "4/10", status: "open" },
    { id: 2, venue: "OSiR Wola", date: "Jutro, 20:00", price: "20 PLN", slots: "10/10", status: "full" }
  ]);

  const tg = window.Telegram.WebApp;
  const telegramId = tg.initDataUnsafe?.user?.id || 12345678;

  useEffect(() => {
    tg.ready();
    tg.expand();
    // Ustawienie kolorów status baru w Telegramie
    tg.setHeaderColor(tg.colorScheme === 'dark' ? '#1A1A1A' : '#ffffff');
    tg.setBackgroundColor(tg.colorScheme === 'dark' ? '#1A1A1A' : '#ffffff');
  }, []);

  return (
    <div className="min-h-screen bg-white dark:bg-[#1A1A1A] font-sans selection:bg-babyBlue selection:text-white transition-colors duration-300">
      <Header />

      <main className="p-6 max-w-lg mx-auto pb-32">
        {activeTab === 'play' ? (
          <>
            {/* WELCOME BANNER */}
            <div className={`mb-8 p-6 rounded-3xl border-2 transition-all duration-300 relative overflow-hidden ${wallet ? 'bg-babyGreen/5 border-babyGreen/30 dark:bg-babyGreen/5 dark:border-babyGreen/20' : 'bg-babyBlue/5 border-babyBlue/20 dark:bg-white/5 dark:border-white/10'}`}>
              
              {/* Dekoracyjne tło */}
              <div className={`absolute -top-10 -right-10 w-32 h-32 rounded-full blur-3xl opacity-20 ${wallet ? 'bg-babyGreen' : 'bg-babyBlue'}`}></div>

              <div className="flex items-center gap-4 mb-2 relative z-10">
                <div className={`p-3 rounded-2xl ${wallet ? 'bg-babyGreen/20 text-green-600 dark:text-green-400' : 'bg-babyBlue/20 text-babyBlue'}`}>
                    {wallet ? <Activity size={24} /> : <Trophy size={24} />}
                </div>
                <div>
                    <h2 className="font-bold text-xl text-gray-900 dark:text-white leading-tight">
                        {wallet ? 'Gotowy do gry!' : 'Witaj w grze!'}
                    </h2>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                        {wallet ? 'Portfel podłączony • Konto aktywne' : 'Zaloguj się, aby zagrać'}
                    </p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between px-2 mb-2">
                 <h3 className="font-bold text-lg text-gray-900 dark:text-white">Dostępne mecze</h3>
                 <span className="text-sm font-semibold text-babyBlue cursor-pointer">Zobacz wszystkie</span>
              </div>
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
          <ProfileView telegramId={telegramId} />
        )}
      </main>

      {/* BOTTOM NAV - Glassmorphism */}
      <nav className="fixed bottom-6 left-6 right-6 bg-white/90 dark:bg-[#2C2C2C]/90 backdrop-blur-xl border border-gray-100 dark:border-white/10 px-8 py-4 rounded-3xl flex justify-between items-center z-40 shadow-[0_10px_40px_rgb(0,0,0,0.1)] dark:shadow-[0_10px_40px_rgb(0,0,0,0.3)]">
        
        <button 
          onClick={() => setActiveTab('play')}
          className={`group flex flex-col items-center gap-1 transition-all ${activeTab === 'play' ? 'scale-110' : 'opacity-50 hover:opacity-100'}`}
        >
          <Calendar size={28} className={activeTab === 'play' ? 'text-babyBlue dark:text-babyOrange fill-current' : 'text-gray-400 dark:text-white'} strokeWidth={2.5} />
        </button>

        {/* Floating Action Button */}
        <button 
          className="bg-black dark:bg-babyOrange text-white dark:text-black p-4 rounded-full -mt-12 shadow-xl shadow-gray-400/30 dark:shadow-babyOrange/30 border-4 border-white dark:border-[#1A1A1A] transform active:scale-95 transition-transform hover:-translate-y-1"
        >
          <PlusCircle size={32} />
        </button>

        <button 
          onClick={() => setActiveTab('profile')}
          className={`group flex flex-col items-center gap-1 transition-all ${activeTab === 'profile' ? 'scale-110' : 'opacity-50 hover:opacity-100'}`}
        >
           <User size={28} className={activeTab === 'profile' ? 'text-babyBlue dark:text-babyOrange fill-current' : 'text-gray-400 dark:text-white'} strokeWidth={2.5} />
        </button>
      </nav>
    </div>
  );
}

export default App;
