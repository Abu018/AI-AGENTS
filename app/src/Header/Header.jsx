import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const Header = () => {
  const navigate = useNavigate();

  return (
    <div className="bg-gray-900">
      <header className="cursor-pointer relative flex justify-between py-4 text-white">
        <div className="ml-20">
          <h1 className="font-mono font-bold " onClick={() => navigate("/")}>
            Codewave
          </h1>
        </div>
      </header>
    </div>
  );
};

export default Header;
//
