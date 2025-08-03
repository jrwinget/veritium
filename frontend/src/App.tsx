import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import HomePage from './components/HomePage'
import AssessmentPage from './components/AssessmentPage'
import SharedAssessmentPage from './components/SharedAssessmentPage'

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="assessment/:id" element={<AssessmentPage />} />
          <Route path="share/:shareId" element={<SharedAssessmentPage />} />
        </Route>
      </Routes>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
    </>
  )
}

export default App