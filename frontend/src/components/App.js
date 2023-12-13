import React from 'react';
import { Routes, Route } from 'react-router-dom';

import '../static/App.css';

import Layout from './Layout.js'

import Home from '../routes/Home.js'
import Players from '../routes/Players.js'


const App = () => {
  return (
    <>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="home" element={<Home />} />
          <Route path="players" element={<Players />} />
          {/* <Route path="teams" element={<Teams />} /> */}
        </Route>
      </Routes>
    </>
  );
};

export default App;
