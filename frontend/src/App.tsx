import { Routes, Route } from 'react-router-dom'
import Landing from '@/pages/Landing'
import Plan from '@/pages/Plan'

function App() {
  return (
    <div>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/plan" element={<Plan />} />
      </Routes>
    </div>
  )
}

export default App
