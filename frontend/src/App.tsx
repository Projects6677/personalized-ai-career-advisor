import InteractiveChatbot from "./components/InteractiveChatbot";

function App() {
  return (
    <div className="flex justify-center items-center min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-50">
      <div className="w-full max-w-2xl p-6 bg-white dark:bg-slate-800 rounded-lg shadow-xl">
        <h1 className="text-3xl font-bold mb-4 text-center">
          🎓 AI Career & Skills Advisor
        </h1>
        <InteractiveChatbot />
      </div>
    </div>
  );
}

export default App;
