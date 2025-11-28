// src/socket.js
import { io } from "socket.io-client";

export const socket = io(import.meta.env.VITE_BACKEND_URL || "http://localhost:5000", {
  transports: ["websocket"],
  reconnectionAttempts: 5,
  reconnectionDelay: 3000,
});