import { useEffect, useState } from 'react'
import './App.css'
import Dashboard from './Dashboard'
import SimulationAnimation from './SimulationAnimation'

function readCsv(text) { const lines = text.trim().split(/\r?\n/); if (lines.length < 2) return []; const headers = lines[0].split(',').map(h => h.trim()); return lines.slice(1).map(line => { const cells = line.split(','); const row = {}; headers.forEach((h, i) => { row[h] = (cells[i] ?? '').trim() }); return row }) }

export default function App() {
    const [restaurants, setRestaurants] = useState([]), [rider, setRider] = useState({ rider_name: '-', busy_rate: 0 }), [order, setOrder] = useState({ count: 0, avg: 0 }), [error, setError] = useState(''), [activeTab, setActiveTab] = useState('overview')
    useEffect(() => { async function load() { try { const [re, ri, or] = await Promise.all([fetch('/restaurant.csv').then(r => { if (!r.ok) throw new Error('restaurant.csv'); return r.text() }), fetch('/rider.csv').then(r => { if (!r.ok) throw new Error('rider.csv'); return r.text() }), fetch('/order.csv').then(r => { if (!r.ok) throw new Error('order.csv'); return r.text() })]); setRestaurants(readCsv(re)); const rr = readCsv(ri); if (rr[0]) setRider(rr[0]); const oo = readCsv(or); setOrder({ count: Number(oo.find(r => r.label === 'order_nums')?.value ?? 0), avg: Number(oo.find(r => r.label === 'average_waiting_time')?.value ?? 0) }) } catch (e) { setError(`Failed to load simulation output: ${e.message}`) } } load() }, [])
    if (error) return <div className="dash"><div className="notice errorNotice">{error}</div></div>
    return <div className="dash"><header className="dashHeader"><div><h1>TakeAway Simulation Dashboard</h1><p className="headerSubtitle">Operational overview of restaurant load, rider utilization and order service performance.</p></div></header><nav className="tabBar"><button className={`tabButton ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>Overview</button><button className={`tabButton ${activeTab === 'animation' ? 'active' : ''}`} onClick={() => setActiveTab('animation')}>Animation</button></nav>{activeTab === 'overview' ? <Dashboard restaurants={restaurants} rider={rider} order={order} /> : <SimulationAnimation />}</div>
}
