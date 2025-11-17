import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import UploadTicketPage from './pages/UploadTicketPage';
import MyTicketsPage from './pages/MyTicketsPage';
import GenerateInvoicePage from './pages/GenerateInvoicePage';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/upload-ticket" element={<UploadTicketPage />} />
        <Route path="/my-tickets" element={<MyTicketsPage />} />
        <Route path="/generate-invoice" element={<GenerateInvoicePage />} />
      </Routes>
    </Router>
  );
}

export default App;
