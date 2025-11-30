import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Navbar, Container, Nav } from 'react-bootstrap';
import HomePage from './pages/HomePage';
import PalletPicking from './pages/PalletPicking';
import PackagePicking from './pages/PackagePicking';
import DeliveryLabels from './pages/DeliveryLabels';

function App() {
  return (
    <Router>
      <div className="d-flex flex-column min-vh-100">
        <Navbar bg="dark" variant="dark" expand="lg" className="shadow-sm">
          <Container>
            <Navbar.Brand as={Link} to="/" className="fw-bold">
              <i className="bi bi-box-seam me-2"></i>
              OSE Picking Portal
            </Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
              <Nav className="ms-auto">
                <Nav.Link as={Link} to="/">
                  <i className="bi bi-house-door me-1"></i>
                  Inicio
                </Nav.Link>
                <Nav.Link as={Link} to="/palets">
                  <i className="bi bi-stack me-1"></i>
                  Palets
                </Nav.Link>
                <Nav.Link as={Link} to="/paquetes">
                  <i className="bi bi-box-seam me-1"></i>
                  Paquetes
                </Nav.Link>
                <Nav.Link as={Link} to="/etiquetas">
                  <i className="bi bi-upc-scan me-1"></i>
                  Etiquetas
                </Nav.Link>
              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        <main className="flex-grow-1 bg-light">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/palets" element={<PalletPicking />} />
            <Route path="/paquetes" element={<PackagePicking />} />
            <Route path="/etiquetas" element={<DeliveryLabels />} />
          </Routes>
        </main>

        <footer className="bg-dark text-white py-3 mt-auto">
          <Container>
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <small>&copy; 2024 OSE Platform - Picking Portal</small>
              </div>
              <div>
                <small className="text-muted">
                  Versión 1.0.0
                </small>
              </div>
            </div>
          </Container>
        </footer>
      </div>
    </Router>
  );
}

export default App;
