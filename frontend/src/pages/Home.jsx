import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import axios from '../lib/axios';
import { StarIcon, ShoppingCartIcon, HeartIcon } from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';

const Home = () => {
  const [email, setEmail] = useState('');
  
  // Fetch featured products
  const { data: featuredProducts, isLoading: productsLoading } = useQuery({
    queryKey: ['featuredProducts'],
    queryFn: async () => {
      const response = await axios.get('/api/products/featured/');
      return response.data;
    }
  });

  // Fetch categories
  const { data: categories, isLoading: categoriesLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await axios.get('/api/categories/');
      return response.data;
    }
  });

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gray-900 h-[600px]">
        <div className="absolute inset-0">
          <img
            src="https://images.unsplash.com/photo-1573855619003-97b4799dcd8b"
            alt="Hero background"
            className="w-full h-full object-cover opacity-40"
          />
        </div>
        <div className="relative max-w-7xl mx-auto py-24 px-4 sm:py-32 sm:px-6 lg:px-8">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl"
          >
            New Season Arrivals
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="mt-6 text-xl text-gray-300 max-w-3xl"
          >
            Discover the latest trends and must-have items for your wardrobe.
            Shop now and get free shipping on orders over $50.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="mt-10"
          >
            <Link
              to="/shop"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-gray-900 bg-white hover:bg-gray-100"
            >
              Shop Now
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-extrabold tracking-tight text-gray-900">
          Shop by Category
        </h2>
        <div className="mt-6 grid grid-cols-1 gap-y-6 gap-x-6 sm:grid-cols-2 lg:grid-cols-4">
          {categoriesLoading ? (
            Array(4).fill(0).map((_, index) => (
              <div key={index} className="animate-pulse">
                <div className="h-64 bg-gray-200 rounded-lg"></div>
                <div className="h-4 bg-gray-200 rounded mt-4 w-3/4"></div>
              </div>
            ))
          ) : categories?.map((category) => (
            <Link
              key={category.id}
              to={`/category/${category.slug}`}
              className="group relative"
            >
              <div className="relative w-full h-64 rounded-lg overflow-hidden">
                <img
                  src={category.image}
                  alt={category.name}
                  className="w-full h-full object-cover object-center group-hover:opacity-75 transition-opacity"
                />
                <div className="absolute inset-0 bg-black bg-opacity-25 flex items-center justify-center">
                  <h3 className="text-2xl font-bold text-white">{category.name}</h3>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Featured Products Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 bg-gray-50">
        <h2 className="text-3xl font-extrabold tracking-tight text-gray-900">
          Featured Products
        </h2>
        <div className="mt-6 grid grid-cols-1 gap-y-10 gap-x-6 sm:grid-cols-2 lg:grid-cols-4">
          {productsLoading ? (
            Array(4).fill(0).map((_, index) => (
              <div key={index} className="animate-pulse">
                <div className="h-80 bg-gray-200 rounded-lg"></div>
                <div className="h-4 bg-gray-200 rounded mt-4"></div>
                <div className="h-4 bg-gray-200 rounded mt-2 w-1/2"></div>
              </div>
            ))
          ) : featuredProducts?.map((product) => (
            <motion.div
              key={product.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="group relative"
            >
              <div className="relative w-full h-80 rounded-lg overflow-hidden">
                <img
                  src={product.image}
                  alt={product.name}
                  className="w-full h-full object-cover object-center group-hover:opacity-75"
                />
                <div className="absolute top-2 right-2 space-y-2">
                  <button className="p-2 rounded-full bg-white shadow-md hover:bg-gray-100">
                    <HeartIcon className="h-5 w-5 text-gray-600" />
                  </button>
                  <button className="p-2 rounded-full bg-white shadow-md hover:bg-gray-100">
                    <ShoppingCartIcon className="h-5 w-5 text-gray-600" />
                  </button>
                </div>
              </div>
              <div className="mt-4 flex justify-between">
                <div>
                  <h3 className="text-sm font-medium text-gray-900">
                    <Link to={`/product/${product.id}`}>
                      {product.name}
                    </Link>
                  </h3>
                  <div className="mt-1 flex items-center">
                    {[0, 1, 2, 3, 4].map((rating) => (
                      <StarIcon
                        key={rating}
                        className={`${
                          product.rating > rating ? 'text-yellow-400' : 'text-gray-200'
                        } h-4 w-4 flex-shrink-0`}
                        aria-hidden="true"
                      />
                    ))}
                    <span className="ml-1 text-sm text-gray-500">
                      ({product.reviewCount})
                    </span>
                  </div>
                </div>
                <p className="text-sm font-medium text-gray-900">${product.price}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Special Offers Section */}
      <section className="relative py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="relative bg-gray-900 rounded-lg overflow-hidden">
            <div className="absolute inset-0">
              <img
                src="https://images.unsplash.com/photo-1614179924047-e1ab49a0a0cf"
                alt="Special offers background"
                className="w-full h-full object-cover opacity-40"
              />
            </div>
            <div className="relative py-16 px-6 sm:py-24 sm:px-12 lg:px-16">
              <div className="md:ml-auto md:w-1/2 md:pl-10">
                <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
                  Summer Sale
                </h2>
                <p className="mt-6 text-lg text-gray-300">
                  Get up to 50% off on selected items. Limited time offer.
                  Don't miss out on these amazing deals!
                </p>
                <div className="mt-8">
                  <Link
                    to="/sale"
                    className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-gray-900 bg-white hover:bg-gray-100"
                  >
                    View Offers
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Newsletter Section */}
      <section className="bg-gray-800">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8">
          <div className="px-6 py-6 rounded-lg md:py-12 md:px-12 lg:py-16 lg:px-16 xl:flex xl:items-center">
            <div className="xl:w-0 xl:flex-1">
              <h2 className="text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
                Want to stay updated?
              </h2>
              <p className="mt-3 max-w-3xl text-lg leading-6 text-gray-300">
                Sign up for our newsletter to receive exclusive offers and the latest news.
              </p>
            </div>
            <div className="mt-8 sm:w-full sm:max-w-md xl:mt-0 xl:ml-8">
              <form className="sm:flex">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="w-full px-5 py-3 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white rounded-md"
                />
                <button
                  type="submit"
                  className="mt-3 w-full flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:flex-shrink-0"
                >
                  Subscribe
                </button>
              </form>
              <p className="mt-3 text-sm text-gray-300">
                We care about your data. Read our{' '}
                <Link to="/privacy" className="font-medium text-white hover:text-gray-200">
                  Privacy Policy
                </Link>
                .
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;