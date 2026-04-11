import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyBefsivb2JZ9qSzHPaRHw9EabzX-vQswWM",
  authDomain: "resume-analyzer-2a618.firebaseapp.com",
  projectId: "resume-analyzer-2a618",
  storageBucket: "resume-analyzer-2a618.appspot.com",
  messagingSenderId: "636617300689",
  appId: "1:636617300689:web:ec1496a6de4c6e49a383f0"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export { app };
