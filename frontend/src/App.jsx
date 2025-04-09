import { useState } from 'react';
import './App.css';

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [step, setStep] = useState('login'); // login, semesters, modules, downloading, completed, error
  const [semesters, setSemesters] = useState([]);
  const [modules, setModules] = useState([]);
  const [selectedSemester, setSelectedSemester] = useState(null);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(0);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage("Logging in...");

    try {
      const res = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (data.success) {
        setSemesters(data.semesters);
        setStep('semesters');
        setMessage("");
      } else {
        setMessage("Error: " + (data.error || "Failed to login"));
      }
    } catch (err) {
      console.error("Fetch failed:", err);
      setMessage("An unexpected error occurred. Please check your connection and try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectSemester = async (semester) => {
    setSelectedSemester(semester);
    setIsLoading(true);
    setMessage("Loading modules...");

    try {
      const res = await fetch('http://localhost:5000/modules', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          password,
          semester_id: semester.id
        }),
      });

      const data = await res.json();

      if (data.success) {
        setModules(data.modules);
        setStep('modules');
        setMessage("");
      } else {
        setMessage("Error: " + (data.error || "Failed to load modules"));
      }
    } catch (err) {
      console.error("Fetch failed:", err);
      setMessage("An unexpected error occurred. Please check your connection and try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadModule = async (moduleUrl, moduleName) => {
    setMessage("");
    setStep('downloading');
    setIsLoading(true);
    setDownloadProgress(0);

    // Simulate download progress
    const progressInterval = setInterval(() => {
      setDownloadProgress(prev => {
        const newProgress = prev + Math.random() * 10;
        return newProgress >= 95 ? 95 : newProgress;
      });
    }, 1000);

    try {
      const res = await fetch('http://localhost:5000/download', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          password,
          module_url: moduleUrl,
          module_name: moduleName
        }),
      });

      // Clear the interval regardless of response
      clearInterval(progressInterval);
      setDownloadProgress(100);
      
      const text = await res.text();

      if (res.ok) {
        setStep('completed');
        setMessage(text);
      } else {
        setStep('error');
        setMessage("Error: " + text);
      }
    } catch (err) {
      clearInterval(progressInterval);
      console.error("Fetch failed:", err);
      setStep('error');
      setMessage("An unexpected error occurred. Please check your connection and try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const renderLoginForm = () => (
    <form onSubmit={handleLogin} className="login-form">
      <h2>Login to Moodle</h2>
      <div className="form-group">
        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          className="form-control"
          disabled={isLoading}
        />
      </div>
      <div className="form-group">
        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="form-control"
          disabled={isLoading}
        />
      </div>
      <button 
        type="submit" 
        className="btn btn-primary"
        disabled={isLoading}
      >
        {isLoading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );

  const renderSemesters = () => {
    // Group semesters by department
    const commonCore = semesters.filter(sem => sem.name.includes("Common Core"));
    const computerEng = semesters.filter(sem => sem.name.includes("Computer Engineering"));
    const otherSemesters = semesters.filter(
      sem => !sem.name.includes("Common Core") && !sem.name.includes("Computer Engineering")
    );

    return (
      <div className="semesters-container">
        <h2>Select Semester</h2>

        {commonCore.length > 0 && (
          <div className="department-group">
            <h3>Common Core</h3>
            <div className="semester-list">
              {commonCore.map((semester) => (
                <div
                  key={semester.id}
                  className="semester-item"
                  onClick={() => handleSelectSemester(semester)}
                >
                  {semester.name.split('(')[0].trim()}
                </div>
              ))}
            </div>
          </div>
        )}

        {computerEng.length > 0 && (
          <div className="department-group">
            <h3>Computer Engineering</h3>
            <div className="semester-list">
              {computerEng.map((semester) => (
                <div
                  key={semester.id}
                  className="semester-item"
                  onClick={() => handleSelectSemester(semester)}
                >
                  {semester.name.split('(')[0].trim()}
                </div>
              ))}
            </div>
          </div>
        )}

        {otherSemesters.length > 0 && (
          <div className="department-group">
            <h3>Other Courses</h3>
            <div className="semester-list">
              {otherSemesters.map((semester) => (
                <div
                  key={semester.id}
                  className="semester-item"
                  onClick={() => handleSelectSemester(semester)}
                >
                  {semester.name.split('(')[0].trim()}
                </div>
              ))}
            </div>
          </div>
        )}

        <button 
          onClick={() => setStep('login')} 
          className="btn btn-secondary"
          disabled={isLoading}
        >
          Back to Login
        </button>
      </div>
    );
  };

  const renderModules = () => (
    <div className="modules-container">
      <h2>
        {selectedSemester && selectedSemester.name.split('(')[0].trim()} - Modules
      </h2>
      <div className="module-list">
        {modules.map((module) => (
          <div key={module.id} className="module-item">
            <h3>{module.name}</h3>
            <p><strong>Teachers:</strong> {module.teachers.join(', ')}</p>
            <button
              onClick={() => handleDownloadModule(module.url, module.name)}
              className="btn btn-success"
              disabled={isLoading}
            >
              Download All Materials
            </button>
          </div>
        ))}
      </div>
      <button 
        onClick={() => setStep('semesters')} 
        className="btn btn-secondary"
        disabled={isLoading}
      >
        Back to Semesters
      </button>
    </div>
  );

  const renderDownloadingProgress = () => (
    <div className="download-progress">
      <h2>Downloading Materials</h2>
      <div className="loading-container">
        <p className="loading-text">Downloading files from Moodle...</p>
        <div className="loading-spinner"></div>
      </div>
      <div className="progress-bar-container">
        <div 
          className="progress-bar" 
          style={{ width: `${downloadProgress}%` }}
        ></div>
        <div className="progress-text">{Math.round(downloadProgress)}%</div>
      </div>
      <p>This may take a few minutes depending on file sizes.</p>
      <p>Files will be organized in module-specific folders.</p>
    </div>
  );

  const renderCompletedDownload = () => (
    <div className="download-complete">
      <h2>Download Complete!</h2>
      <div className="success-icon">✓</div>
      <div className="message">{message}</div>
      <button
        onClick={() => setStep('modules')}
        className="btn btn-primary"
      >
        Return to Modules
      </button>
    </div>
  );

  const renderErrorState = () => (
    <div className="download-error">
      <h2>Download Error</h2>
      <div className="error-icon">✗</div>
      <div className="message">{message}</div>
      <button
        onClick={() => setStep('modules')}
        className="btn btn-primary"
      >
        Return to Modules
      </button>
    </div>
  );

  return (
    <div className="container">
      <h1>Moodle Downloader</h1>

      {step === 'login' && renderLoginForm()}
      {step === 'semesters' && renderSemesters()}
      {step === 'modules' && renderModules()}
      {step === 'downloading' && renderDownloadingProgress()}
      {step === 'completed' && renderCompletedDownload()}
      {step === 'error' && renderErrorState()}

      {message && step !== 'completed' && step !== 'error' && (
        <div className="message">{message}</div>
      )}
    </div>
  );
}

export default App;