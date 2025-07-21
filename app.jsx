const { useState, useEffect } = React

const App = () => {
	const [menu, setMenu] = useState([])
	const [page, setPage] = useState("index")
	const [anchor, setAnchor] = useState()

	useEffect(() => {
		fetch("data/menu.json")
			.then((res) => res.json())
			.then(setMenu);

		const updatePage = () => {
			const hash = window.location.hash.replace("#/", "");
			const basepage = hash.split(".")
			setPage(basepage[0] || "index")
			setAnchor(basepage[1])
		}
		window.addEventListener("hashchange", updatePage);
		updatePage();
		return () => window.removeEventListener("hashchange", updatePage);
	}, [])

	return (
		<div className="container mt-4">
			<div className="row">
				<div className="col-md-3">
					<Sidebar menu={menu} />
				</div>
				<div className="col-md-9">
					<Content page={page} anchor={anchor} />
				</div>
			</div>
		</div>
	)
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />)
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
document.documentElement.setAttribute("data-bs-theme", prefersDark ? "dark" : "light")
document.querySelector("#hljs-theme").href = `https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/${
	prefersDark ? "github-dark-dimmed" : "vs"
}.min.css`
