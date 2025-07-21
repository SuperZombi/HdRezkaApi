const { useState, useEffect } = React

const App = () => {
	const [menu, setMenu] = useState([])
	const [page, setPage] = useState("index")

	useEffect(() => {
		fetch("data/menu.json")
			.then((res) => res.json())
			.then(setMenu);

		const updatePage = () => {
			const hash = window.location.hash.replace("#/", "");
			setPage(hash || "index");
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
					<Content page={page} />
				</div>
			</div>
		</div>
	)
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />)
