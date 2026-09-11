import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import './SimulationAnimation.css'

const parseClock = (s) => { const m = s.match(/(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+(?:\.\d+)?)/); if (!m) return 0; return ((Number(m[3]) - 1) * 86400) + Number(m[4]) * 3600 + Number(m[5]) * 60 + Number(m[6]) }
const cloneWorld = w => ({ ...w, rider: { ...w.rider, load: [...w.rider.load] }, restaurants: w.restaurants.map(r => ({ ...r, ready: [...r.ready] })), unassigned: [...w.unassigned] })

function makeWorld(initial) { return { scene: { ...initial.scene }, rider: { ...initial.rider, load: [...(initial.rider.load || [])] }, restaurants: (initial.restaurants || []).map(r => ({ ...r, ready: [...(r.ready || [])] })), unassigned: [...(initial.unassigned_orders || [])], delivered: 0, lastEvent: null } }
function applyEvent(world, e) {
  const w = world; w.lastEvent = e; const restaurant = id => w.restaurants.find(r => Number(r.id) === Number(id));
  if (e.type === 'generate_order') w.unassigned.push(e.order)
  if (e.type === 'order_assigned') { w.unassigned = w.unassigned.filter(x => x !== e.order); const r = restaurant(e.restaurant); if (r) r.cooking = e.order }
  if (e.type === 'cooking_finished') { const r = restaurant(e.restaurant); if (r) { if (r.cooking === e.order) r.cooking = null; if (!r.ready.includes(e.order)) r.ready.push(e.order) } }
  if (e.type === 'receive_order') w.rider.receive = e.order
  if (e.type === 'move_to_pick_up') { w.rider.position = Number(e.current_position); w.rider.state = 'to_pick_up'; w.rider.target_order = e.order; w.rider.receive = e.order }
  if (e.type === 'pick_up') { const at = w.restaurants.find(r => r.ready.includes(e.order)); if (at) w.rider.position = Number(at.position); w.restaurants.forEach(r => { r.ready = r.ready.filter(x => x !== e.order) }); if (!w.rider.load.includes(e.order)) w.rider.load.push(e.order); w.rider.receive = null; w.rider.target_order = null }
  if (e.type === 'move_to_deliver') { w.rider.position = Number(e.current_position); w.rider.state = 'to_deliver'; w.rider.target_order = null }
  if (e.type === 'deliver') { w.rider.position = Number(w.scene?.customer_position ?? 500); w.rider.load = w.rider.load.filter(x => x !== e.order); w.delivered += 1 }
  return w
}

const Icon = ({ type }) => type === 'store' ? <svg viewBox="0 0 48 48"><path d="M8 20v20h32V20M6 19l4-11h28l4 11" /><path d="M13 19v-1m7 1v-1m8 1v-1m7 1v-1M16 40V27h10v13M31 28h5v6h-5z" /></svg> : type === 'home' ? <svg viewBox="0 0 48 48"><path d="M6 23 24 8l18 15v18H29V29H19v12H6z" /></svg> : <svg viewBox="0 0 64 40"><circle cx="16" cy="31" r="7" /><circle cx="50" cy="31" r="7" /><path d="M16 31l10-17h13l11 17M26 14l8 17H16m18 0h16M39 14l7-7h8M25 10h9" /></svg>

function formatTime(seconds) { const d = Math.floor(seconds / 86400) + 1, rem = seconds % 86400, h = Math.floor(rem / 3600), m = Math.floor((rem % 3600) / 60), s = Math.floor(rem % 60); return `Day ${d} · ${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}` }


const restaurantStatus = (r) => ({
  activity: r.cooking != null
    ? { kind: 'cooking', text: `Cooking #${r.cooking}` }
    : { kind: 'idle', text: 'Idle' },

  ready: {
    kind: 'ready',
    text: r.ready.length
      ? `Ready · ${r.ready.map(id => `#${id}`).join(', ')}`
      : 'Ready · —'
  }
})

const riderStatus = (move, rider) => {
  if (move?.type === 'move_to_pick_up') return { kind: 'pickup', text: `Picking up #${move.order}` }
  if (move?.type === 'move_to_deliver') return { kind: 'deliver', text: `Delivering · ${rider.load.length} orders` }
  if (rider.load.length) return { kind: 'carrying', text: `Carrying ${rider.load.length} orders` }
  return { kind: 'idle', text: 'Idle' }
}

export default function SimulationAnimation() {
  const [initial, setInitial] = useState(null), [events, setEvents] = useState([]), [error, setError] = useState(''), [playing, setPlaying] = useState(false), [speed, setSpeed] = useState(60), [simTime, setSimTime] = useState(0), [world, setWorld] = useState(null)
  const worldRef = useRef(null), eventIndex = useRef(0), simRef = useRef(0), lastFrame = useRef(null)
  useEffect(() => { Promise.all([fetch('/animation_initial_state.json').then(r => r.json()), fetch('/animation_events.json').then(r => r.json())]).then(([i, ev]) => { const base = parseClock(i.clock_time); const normalized = ev.map((e, idx) => ({ ...e, _t: parseClock(e.clock_time) - base, _idx: idx })); setInitial(i); setEvents(normalized); const w = makeWorld(i); worldRef.current = w; setWorld(cloneWorld(w)) }).catch(e => setError(`Failed to load animation data: ${e.message}`)) }, [])
  const duration = events.length ? Math.max(0, events[events.length - 1]._t) : 0
  const movementSegments = useMemo(() => {
    if (!initial) return []
    const segs = []

    // Warm-up may end while the rider is already travelling.  The initial
    // snapshot gives the exact position; the first matching arrival event
    // gives the end of that in-progress movement.
    if (initial.rider?.state === 'to_deliver') {
      const firstDeliver = events.find(e => e.type === 'deliver' && e._t >= 0)
      if (firstDeliver) {
        segs.push({
          start: 0,
          end: firstDeliver._t,
          from: Number(initial.rider.position),
          to: Number(initial.scene?.customer_position ?? 500),
          type: 'move_to_deliver',
          order: null,
        })
      }
    }

    for (let i = 0; i < events.length; i++) {
      const e = events[i]
      if (e.type !== 'move_to_pick_up' && e.type !== 'move_to_deliver') continue

      const terminal = e.type === 'move_to_pick_up' ? 'pick_up' : 'deliver'
      let end = e._t

      for (let j = i + 1; j < events.length; j++) {
        const candidate = events[j]
        if (candidate.type !== terminal) continue
        if (terminal === 'deliver' || candidate.order === e.order) {
          end = candidate._t
          break
        }
      }

      segs.push({
        start: e._t,
        end,
        from: Number(e.current_position),
        to: e.type === 'move_to_deliver'
          ? Number(initial.scene?.customer_position ?? 500)
          : Number(e.target_position),
        type: e.type,
        order: e.order,
      })
    }

    return segs
  }, [events, initial])
  const rebuild = useCallback((t) => { if (!initial) return; const w = makeWorld(initial); let idx = 0; while (idx < events.length && events[idx]._t <= t) { applyEvent(w, events[idx]); idx++ } worldRef.current = w; eventIndex.current = idx; simRef.current = t; setWorld(cloneWorld(w)); setSimTime(t) }, [initial, events])
  useEffect(() => {
    if (!playing) return
    let raf

    const tick = now => {
      if (lastFrame.current == null) lastFrame.current = now
      const dt = (now - lastFrame.current) / 1000
      lastFrame.current = now

      const next = Math.min(duration, simRef.current + dt * speed)
      let worldChanged = false

      while (eventIndex.current < events.length && events[eventIndex.current]._t <= next) {
        applyEvent(worldRef.current, events[eventIndex.current])
        eventIndex.current++
        worldChanged = true
      }

      simRef.current = next
      setSimTime(next)
      if (worldChanged) setWorld(cloneWorld(worldRef.current))

      if (next >= duration) {
        setPlaying(false)
        lastFrame.current = null
        return
      }
      raf = requestAnimationFrame(tick)
    }

    raf = requestAnimationFrame(tick)
    return () => {
      cancelAnimationFrame(raf)
      lastFrame.current = null
    }
  }, [playing, speed, duration, events])
  const move = useMemo(
    () => movementSegments.find(s => simTime >= s.start && simTime <= s.end),
    [movementSegments, simTime]
  )
  const scene = initial?.scene
  const roadStart = Number(scene?.road_start ?? 0)
  const roadEnd = Number(scene?.road_end ?? 500)

  let riderPos = Number(world?.rider?.position ?? roadStart)
  if (move) {
    const rawProgress = move.end === move.start
      ? 1
      : (simTime - move.start) / (move.end - move.start)
    const progress = Math.max(0, Math.min(1, rawProgress))
    riderPos = move.from + (move.to - move.from) * progress
  }
  const posPct = x => `${Math.max(2, Math.min(98, ((x - roadStart) / (roadEnd - roadStart)) * 100))}%`
  const direction = move && move.to < move.from ? -1 : 1
  const currentRiderStatus = world ? riderStatus(move, world.rider) : { kind: 'idle', text: 'Idle' }
  if (error) return <div className="notice errorNotice">{error}</div>; if (!initial || !world) return <section className="card animationCard"><div className="animationLoading">Loading simulation playback…</div></section>
  return <section className="card animationCard"><div className="sectionHeader animationHeader"><div><h2>Simulation Playback</h2><div className="subtle">Watch restaurant activity, rider movement and order delivery over simulation time.</div></div><span className="timeBadge">{formatTime(simTime)}</span></div>
    <div className="scene"><div className="road"><div className="roadCenter" />{world.restaurants.map((r, i) => {
      const status = restaurantStatus(r)
      return <div key={r.id} className={`place restaurantPlace ${i % 2 === 0 ? 'above' : 'below'}`} style={{ left: posPct(r.position) }}>
        <div className="placeCard">
          <span className="placeIcon storeIcon"><Icon type="store" /></span>
          <strong>Restaurant {r.id}</strong>
          <div className="restaurantStatusLines">
            <span className={`placeStatus statusText ${status.activity.kind}`}>
              {status.activity.text}
            </span>

            <span className="placeStatus statusText ready">
              {status.ready.text}
            </span>
          </div>
          {r.ready.length > 0 && <span className="orderBubble">{r.ready.length}</span>}
        </div>
        <span className="connector" />
      </div>
    })}
      <div className="place customerPlace below" style={{ left: posPct(scene.customer_position) }}><div className="placeCard"><span className="placeIcon homeIcon"><Icon type="home" /></span><strong>Customer</strong><span className="placeStatus">{world.delivered} delivered</span></div><span className="connector" /></div>
      <div className="rider" style={{ left: posPct(riderPos) }}>
        <div className="riderLabel">
          <strong>{world.rider.name}</strong>
          <span className={`statusText ${currentRiderStatus.kind}`}>{currentRiderStatus.text}</span>
        </div>
        <div className="bikeWrap">
          <div className="bike" style={{ transform: `scaleX(${direction})` }}><Icon type="bike" /></div>
          {world.rider.load.length > 0 && <span className="loadBubble">{world.rider.load.length}</span>}
        </div>
      </div>
    </div></div>
    <div className="playback"><button className="playButton" onClick={() => { if (simTime >= duration) rebuild(0); setPlaying(p => !p) }} aria-label={playing ? 'Pause' : 'Play'}>{playing ? 'Ⅱ' : '▶'}</button><input className="timeline" type="range" min="0" max={duration || 1} step="1" value={simTime} onChange={e => { setPlaying(false); rebuild(Number(e.target.value)) }} /><div className="timelineTimes"><span>{formatTime(simTime)}</span><span>{formatTime(duration)}</span></div><div className="speedGroup"><span>Speed</span>{[30, 60, 120, 240].map((v, i) => <button key={v} className={speed === v ? 'active' : ''} onClick={() => setSpeed(v)}>{[0.5, 1, 2, 4][i]}×</button>)}</div><button className="resetButton" onClick={() => { setPlaying(false); rebuild(0) }}>↺ Reset</button></div>
  </section>
}
