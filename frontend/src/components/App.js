import React from 'react';
import { Routes, Route } from 'react-router-dom';

import '../static/App.css';

import Layout from './Layout.js'

import Players from '../routes/Players.js'


const App = () => {
  return (
    <>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Players />} />
          <Route path="players" element={<Players />} />
        </Route>
      </Routes>
    </>
  );
};

export default App;
