const Content = ({ page }) => {
	const [data, setData] = React.useState(null)
	const [status, setStatus] = React.useState(200)

	React.useEffect(()=>{
		setData(null)
		setStatus(200)
		fetch(`data/${page}.json`)
			.then(res => {
				setStatus(res.status);
				return res.json()
			})
			.then(setData)
			.catch(() => setData(null))
	}, [page])

	if (status != 200) return <NotFound/>
	if (!data) return <Loading/>;

	return (
		<div>
			<h1 className="mb-3">
				{data.icon && <i className={`fas ${data.icon} me-2`}></i>}
				{data.title}
			</h1>
			<Text>{data.description}</Text>
			<Code lang="javascript">
				{`{translator_id: {translator_name, seasons: {1, 2}, episodes: {1: {1, 2, 3}, 2: {1, 2, 3}}}}`}
			</Code>
			<Code lang="python">
				{`rezka = HdRezkaApi('...')\nprint(rezka.name)`}
			</Code>
		</div>
	)
}
