const KEY = 'admin-mock-v1';

const defaultState = {
  metrics: {
    totalUsers: 123,
    totalRoutines: 456,
    publicRoutines: 300,
    privateRoutines: 156,
    freeUsers: 90,
    premiumUsers: 33
  },

  recent: [
    { id:1, text: 'Usuario X creó rutina "Mañana en 5"', date: Date.now() - 1000*60*60 },
    { id:2, text: 'Rutina pública aprobada: "Cardio 10"', date: Date.now() - 1000*60*30 }
  ],

  // 🔥 ahora son objetos
  categories: [
    { id:1, name:'Cardio' },
    { id:2, name:'Mindfulness' }
  ],

  // 🔥 hábitos sugeridos por categoría
  habits: [
    { id:1, categoryId:1, name:'Caminar 10 minutos' },
    { id:2, categoryId:2, name:'Respiración consciente' }
  ],

  types: ['Mañana','Tarde','Noche'],

  phrases: [
    {id:1, text:'Sigue así', active:true}
  ],

  freemium: {
    trialDays: 14,
    freeLimits: { routinesPerDay: 3 },
    activeFeatures: {}
  },

  system: {
    virtualPet: true,
    recommendations: true,
    notices: []
  }
};

function read() {
  const raw = localStorage.getItem(KEY);

  if (!raw) {
    localStorage.setItem(KEY, JSON.stringify(defaultState));
    return defaultState;
  }

  return JSON.parse(raw);
}

function write(state) {
  localStorage.setItem(KEY, JSON.stringify(state));
  return state;
}

/* ===========================
   DASHBOARD
=========================== */

export function getMetrics() {
  return Promise.resolve(read().metrics);
}

export function getRecentActivity() {
  return Promise.resolve(read().recent);
}

/* ===========================
   CATEGORÍAS
=========================== */

export function getCategories(){
  return Promise.resolve(read().categories);
}

export function addCategory(name){
  const s = read();

  s.categories.push({
    id: Date.now(),
    name
  });

  write(s);
  return Promise.resolve();
}

export function deleteCategory(id){
  const s = read();

  s.categories = s.categories.filter(c => c.id !== id);
  s.habits = s.habits.filter(h => h.categoryId !== id);

  write(s);
  return Promise.resolve();
}

/* ===========================
   HABITOS POR CATEGORIA 🔥
=========================== */

export function getHabitsByCategory(categoryId){
  const s = read();

  return Promise.resolve(
    s.habits.filter(h => h.categoryId === categoryId)
  );
}

export function addHabitToCategory(categoryId, name){
  const s = read();

  s.habits.push({
    id: Date.now(),
    categoryId,
    name
  });

  write(s);
  return Promise.resolve();
}

export function deleteHabit(habitId){
  const s = read();

  s.habits = s.habits.filter(h => h.id !== habitId);

  write(s);
  return Promise.resolve();
}

/* ===========================
   TIPOS
=========================== */

export function getTypes(){
  return Promise.resolve(read().types);
}

export function addType(t){
  const s = read();
  s.types.push(t);
  write(s);
  return Promise.resolve();
}

/* ===========================
   FRASES
=========================== */

export function getPhrases(){
  return Promise.resolve(read().phrases);
}

export function addPhrase(p){
  const s = read();
  s.phrases.push(p);
  write(s);
  return Promise.resolve();
}

export function togglePhrase(id){
  const s = read();
  const ph = s.phrases.find(x=>x.id===id);

  if(ph) ph.active = !ph.active;

  write(s);
  return Promise.resolve();
}

/* ===========================
   FREEMIUM
=========================== */

export function getFreemium(){
  return Promise.resolve(read().freemium);
}

export function updateFreemium(payload){
  const s = read();
  s.freemium = {...s.freemium,...payload};
  write(s);
  return Promise.resolve();
}

/* ===========================
   SISTEMA
=========================== */

export function getSystem(){
  return Promise.resolve(read().system);
}

export function updateSystem(payload){
  const s = read();
  s.system = {...s.system,...payload};
  write(s);
  return Promise.resolve();
}
