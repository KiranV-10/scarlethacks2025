"use client";

import { useState, useEffect } from "react";
import toast from "react-hot-toast";

export default function ProfilePage() {
  const [form, setForm] = useState({
    userId: "",
    gender: "",
    height: "",
    weight: "",
    dateOfBirth: "",
  });

  useEffect(() => {
    // Autofill userId from localStorage (simulate auth token or session)
    const storedUserId = localStorage.getItem("userId");
    if (storedUserId) {
      setForm((prevForm) => ({ ...prevForm, userId: storedUserId }));
    } else {
      toast.error("No user ID found. Please set userId in localStorage.");
    }
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:8000/profiles", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      if (response.ok) {
        const data = await response.json();
        toast.success("Profile created successfully!");
        console.log(data);
        setForm({
          userId: form.userId,
          gender: "",
          height: "",
          weight: "",
          dateOfBirth: "",
        });
      } else {
        const errorData = await response.json();
        toast.error(errorData.detail || "Error creating profile.");
      }
    } catch (error) {
      toast.error(error.message || "Something went wrong.");
    }
  };

  return (
    <div className="max-w-md mx-auto mt-12 p-6 bg-white rounded-xl shadow-md space-y-4">
      <h1 className="text-2xl font-bold text-center">Create Health Profile</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          name="userId"
          placeholder="User ID"
          value={form.userId}
          onChange={handleChange}
          className="w-full border border-gray-300 p-2 rounded"
          readOnly // Prevent manual editing if autofilled
        />

        <select
          name="gender"
          value={form.gender}
          onChange={handleChange}
          className="w-full border border-gray-300 p-2 rounded"
        >
          <option value="">Select Gender</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
        </select>

        <input
          type="number"
          name="height"
          placeholder="Height (cm)"
          value={form.height}
          onChange={handleChange}
          className="w-full border border-gray-300 p-2 rounded"
        />

        <input
          type="number"
          name="weight"
          placeholder="Weight (kg)"
          value={form.weight}
          onChange={handleChange}
          className="w-full border border-gray-300 p-2 rounded"
        />

        <input
          type="date"
          name="dateOfBirth"
          value={form.dateOfBirth}
          onChange={handleChange}
          className="w-full border border-gray-300 p-2 rounded"
        />

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
        >
          Create Profile
        </button>
      </form>
    </div>
  );
}
