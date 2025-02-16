import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-primary text-white shadow-lg">
      <div className="container mx-auto px-4 py-3">
        <div className="flex justify-between items-center">
          <Link to="/" className="text-xl font-bold hover:text-accent">
            E-Commerce
          </Link>
          <div className="flex space-x-6">
            <Link to="/" className="hover:text-accent transition-colors">
              Home
            </Link>
            <Link to="/products" className="hover:text-accent transition-colors">
              Products
            </Link>
            <Link to="/cart" className="hover:text-accent transition-colors">
              Cart
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;