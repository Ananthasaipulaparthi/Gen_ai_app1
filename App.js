import React, { useState } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";

function App() {
    const [file, setFile] = useState(null);
    const [notes, setNotes] = useState([]);
    const [chartData, setChartData] = useState(null);

    const uploadFile = async () => {
        if (!file) {
            alert("Please upload a file");
            return;
        }
        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });
            setNotes(response.data);

            const times = response.data.map((note) => note.time);
            const swaras = response.data.map((note) => note.swara);
            setChartData({
                labels: times,
                datasets: [
                    {
                        label: "Carnatic Notes",
                        data: swaras.map((swara) => swara.length),
                        borderColor: "rgba(75,192,192,1)",
                        borderWidth: 2,
                        fill: false,
                    },
                ],
            });
        } catch (error) {
            console.error(error);
            alert("Error uploading file");
        }
    };

    return (
        <div className="App">
            <h1>Carnatic Notes Extractor</h1>
            <input type="file" onChange={(e) => setFile(e.target.files[0])} />
            <button onClick={uploadFile}>Upload and Process</button>

            {chartData && (
                <div>
                    <h2>Timeline of Swaras</h2>
                    <Line data={chartData} />
                </div>
            )}

            <h2>Extracted Notes</h2>
            <ul>
                {notes.map((note, index) => (
                    <li key={index}>
                        {note.swara} at {note.time.toFixed(2)} seconds
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default App;
