// Entry point: mount the <App /> component into <div id="root"> from index.html.
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import './App.css'

createRoot(document.getElementById('root')).render(<App />)
