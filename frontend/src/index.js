import React from 'react';
import ReactDOM from 'react-dom/client';

import App from './components/App.js';
import './static/App.css'

import { BrowserRouter } from "react-router-dom";




const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
      <BrowserRouter basename="/">
	<App />
    </BrowserRouter>
  </React.StrictMode>
);

