import { useState } from "react";

const Home = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile);
      setError(null);
    } else {
      setError("Please select a valid PDF file.");
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("No file selected");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("pdf", file);

    try {
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to process file");
      }

      setResult({
        filename: data.filename,
        analysis: data.result,
        rawData: data, // Store the complete response for debugging
      });
    } catch (error) {
      console.error("Error:", error);
      setError(error.message || "An error occurred while processing the file");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResult(null);
    setError(null);
  };

  const formatAnalysis = (analysis) => {
    if (typeof analysis === "string") {
      return analysis;
    }

    try {
      if (analysis.output) {
        return analysis.output;
      }
      return JSON.stringify(analysis, null, 2);
    } catch {
      return "Analysis results";
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center text-white px-4">
      <div className="text-center">
        <h1 className="text-6xl font-gupter font-semibold">
          DESIGN WITH PRINCIPLE
        </h1>
      </div>

      <div className="mt-10">
        <div className="flex flex-wrap justify-center gap-4">
          {"CODEWAVE".split("").map((letter, index) => (
            <span
              key={index}
              className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl xl:text-9xl font-bold transition-transform transform hover:-translate-y-1"
            >
              {letter}
            </span>
          ))}
        </div>
      </div>

      <div className="mt-10 p-6 bg-gray-800 rounded-lg shadow-lg w-full max-w-md flex flex-col items-center">
        <label className="text-lg font-medium mb-3">Upload a PDF File</label>
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          className="p-3 w-full bg-gray-700 text-white border border-gray-600 rounded-lg cursor-pointer hover:bg-gray-600 transition"
        />
        {file && (
          <p className="mt-3 text-green-400">Selected File: {file.name}</p>
        )}

        {error && <p className="mt-3 text-red-400">{error}</p>}

        <div className="mt-4 flex gap-4">
          <button
            onClick={handleUpload}
            className={`px-6 py-2 rounded-lg transition ${
              loading
                ? "bg-gray-500 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-500"
            }`}
            disabled={loading}
          >
            {loading ? "Processing..." : "Upload"}
          </button>
          <button
            onClick={handleReset}
            className="px-6 py-2 bg-red-600 rounded-lg hover:bg-red-500 transition"
          >
            Reset
          </button>
        </div>
      </div>

      {result && (
        <div className="mt-10 p-6 bg-gray-700 rounded-lg shadow-lg w-full max-w-3xl text-left">
          <h2 className="text-2xl font-bold mb-4">Resume Analysis Results</h2>
          <p className="mb-2">
            <span className="font-semibold">File Name:</span> {result.filename}
          </p>

          <div className="mt-4 p-4 bg-gray-600 rounded-lg">
            <h3 className="text-xl font-semibold mb-2">Analysis:</h3>
            <div className="whitespace-pre-wrap bg-gray-800 p-4 rounded">
              {formatAnalysis(result.analysis)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;
