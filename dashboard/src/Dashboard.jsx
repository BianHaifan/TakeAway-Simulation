import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import kangarooImage from './assets/kangaroo.jpg'

const pct = (value, digits = 1) => `${(Number(value || 0) * 100).toFixed(digits)}%`

function MetricCard({ label, value, detail }) {
  return <section className="card metricCard"><div className="subtle">{label}</div><div className="metric">{value}</div><div className="subtle">{detail}</div></section>
}

function RestaurantBar({ data }) {
  const rows = data.map(r => ({ name: `Restaurant ${r.restaurant_id}`, busy_rate: Number(r.busy_rate) })).sort((a, b) => b.busy_rate - a.busy_rate)
  return <ResponsiveContainer width="100%" height={400}><BarChart data={rows} layout="vertical" margin={{ top: 12, right: 28, left: 14, bottom: 18 }}>
    <CartesianGrid stroke="#e2e8f0" horizontal={false} /><XAxis type="number" domain={[0, 1]} ticks={[0, .2, .4, .6, .8, 1]} tickFormatter={v => `${Math.round(v * 100)}%`} tick={{ fill: '#64748b', fontSize: 12 }} axisLine={{ stroke: '#cbd5e1' }} tickLine={false} label={{ value: 'Busy Rate', position: 'insideBottom', offset: -10, fill: '#475569', fontSize: 13 }} />
    <YAxis type="category" dataKey="name" width={118} tick={{ fill: '#475569', fontSize: 12 }} axisLine={false} tickLine={false} /><Tooltip formatter={v => [pct(v, 2), 'Busy rate']} contentStyle={{ border: '1px solid #e2e8f0', borderRadius: 8, boxShadow: '0 8px 24px rgba(15,23,42,.10)' }} /><Bar dataKey="busy_rate" name="Busy rate" fill="#f97316" radius={[0, 4, 4, 0]} maxBarSize={26} />
  </BarChart></ResponsiveContainer>
}

function RiderPie({ busyRate }) {
  const busy = Math.min(1, Math.max(0, Number(busyRate))); const data = [{ name: 'Busy', value: busy, color: '#f97316' }, { name: 'Idle', value: Math.max(0, 1 - busy), color: '#0f766e' }]
  return <div className="donutWrap"><ResponsiveContainer width="100%" height={270}><PieChart><Pie data={data} dataKey="value" nameKey="name" innerRadius={66} outerRadius={94} paddingAngle={2} stroke="none">{data.map(e => <Cell key={e.name} fill={e.color} />)}</Pie><Tooltip formatter={v => pct(v, 2)} /><Legend verticalAlign="bottom" iconType="circle" /></PieChart></ResponsiveContainer><div className="donutCenter"><strong>{pct(busy, 1)}</strong><span>Busy</span></div></div>
}

export default function Dashboard({ restaurants, rider, order }) {
  const sorted = restaurants.map(r => ({ ...r, busy: Number(r.busy_rate) })).sort((a, b) => b.busy - a.busy); const busiest = sorted[0]; const avg = sorted.length ? sorted.reduce((s, r) => s + r.busy, 0) / sorted.length : 0
  return <>
    <section className="metricGrid"><MetricCard label="Busiest Restaurant" value={busiest ? `#${busiest.restaurant_id}` : '-'} detail={busiest ? `${pct(busiest.busy, 1)} busy rate` : 'Highest restaurant utilization'} /><MetricCard label="Average Restaurant Busy Rate" value={pct(avg, 1)} detail="Across all restaurants" /><MetricCard label={`Rider ${rider.rider_name} Busy Rate`} value={pct(rider.busy_rate, 1)} detail="Share of simulation time busy" /><MetricCard label="Completed Orders" value={Number(order.count).toLocaleString()} detail="Orders completed in simulation" /><MetricCard label="Average Waiting Time" value={`${Number(order.avg).toFixed(2)} h`} detail="Average order waiting time" /></section>
    <main className="dashboardGrid"><section className="card restaurantCard"><div className="sectionHeader"><div><h2>Restaurants by Busy Rate</h2><div className="subtle">Compare utilization across restaurants in the current simulation.</div></div><span className="badge medium">Utilization</span></div><RestaurantBar data={restaurants} /></section>
      <section className="card"><div className="sectionHeader"><div><h2>Rider Utilization</h2><div className="subtle">Busy and idle share for rider {rider.rider_name}.</div></div><img
        className="riderMascot"
        src={kangarooImage}
        alt="Kangaroo mascot" />
      </div><RiderPie busyRate={rider.busy_rate} /></section>
      <section className="card"><div className="sectionHeader"><div><h2>Order Service Status</h2><div className="subtle">Summary of completed demand and customer waiting.</div></div><span className="badge low">Completed</span></div><div className="statusBox"><div className="statusHeader"><div><span className="subtle">Average Waiting Time</span><strong>{Number(order.avg).toFixed(2)} h</strong></div></div><div className="statusLine"><span className="subtle">Completed orders</span><strong>{Number(order.count).toLocaleString()}</strong></div><div className="statusLine"><span className="subtle">Rider busy rate</span><strong>{pct(rider.busy_rate, 1)}</strong></div></div></section></main>
  </>
}
