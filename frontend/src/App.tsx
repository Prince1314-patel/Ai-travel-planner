import { MotionConfig } from 'framer-motion'
import { Routes, Route } from 'react-router-dom'
import Landing from '@/pages/Landing'

function App() {
  return (
    <MotionConfig reducedMotion="user">
      <div>
        <Routes>
          <Route path="/" element={<Landing />} />
        </Routes>
      </div>
    </MotionConfig>
  )
}

export default App
