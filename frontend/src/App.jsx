import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';

// Temporary page components with Tailwind classes to test
const Home = () => (
  <div className="p-4 bg-gray-100">
    <h1 className="text-2xl font-bold text-primary">Home Page</h1>
  </div>
);
const Products = () => (
  <div className="p-4 bg-gray-100">
    <h1 className="text-2xl font-bold text-primary">Products Page</h1>
  </div>
);
const ProductDetail = () => (
  <div className="p-4 bg-gray-100">
    <h1 className="text-2xl font-bold text-primary">Product Detail Page</h1>
  </div>
);
const Cart = () => (
  <div className="p-4 bg-gray-100">
    <h1 className="text-2xl font-bold text-primary">Cart Page</h1>
  </div>
);
const Checkout = () => (
  <div className="p-4 bg-gray-100">
    <h1 className="text-2xl font-bold text-primary">Checkout Page</h1>
  </div>
);

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-white">
        <Navbar />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 5000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/products" element={<Products />} />
            <Route path="/products/:id" element={<ProductDetail />} />
            <Route path="/cart" element={<Cart />} />
            <Route path="/checkout" element={<Checkout />} />
            <Route path="*" element={
              <div className="p-4 text-center">
                <h1 className="text-2xl font-bold text-red-600">404 Not Found</h1>
              </div>
            } />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;