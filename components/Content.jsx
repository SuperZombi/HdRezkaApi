const Content = ({ page, anchor }) => {
	const [data, setData] = React.useState(null)
	const [status, setStatus] = React.useState(200)

	document.title = "HdRezkaApi Docs";

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

	document.title = `${data.title} • HdRezkaApi`;

	return (
		<div>
			{data.big_icon && <img src={data.big_icon}
				className="float-end"
				style={{height: "64px"}}
			/>}
			<h1 className="mb-3">
				{data.icon && <i className={`fas ${data.icon} me-2`}></i>}
				{data.title}
			</h1>
			<Text>{data.description}</Text>
			{data.sections?.map((section, i) => (
				<Section key={i} data={section} basepath={page} anchor={anchor} />
			))}
		</div>
	)
}

const Section = ({data, basepath, anchor}) => {
	const link = `#/${basepath}.${data.path}`

	React.useEffect(()=>{
		if (anchor) {
			const el = document.querySelector(`[href="#/${basepath}.${anchor}"]:not(.badge)`)
			if (el) {
				const target = el.closest(".card") || el.closest("h3") || el

				let elementPosition = target.getBoundingClientRect().top;
				let offsetPosition = elementPosition - target.offsetHeight / 2
				document.documentElement.scrollBy({top: offsetPosition});

				target.classList.add("highlight")
				setTimeout(_=>{
					target.classList.remove("highlight")
				}, 1000)
			}
		}
	}, [anchor])

	return (
		<div>
			<hr/>
			<h3 className="my-2 pb-2 position-sticky z-2 top-0 bg-body">
				{data.path ? (
					<a href={link} className="text-decoration-none text-reset d-inline-flex align-items-center">
						<i className="fa-solid fa-link me-1" style={{fontSize: "0.75em"}}></i>
						<span>{data.title}</span>
					</a>
				) : data.title}
				{data.icon && <i className={`fas ${data.icon} ms-2`} style={{verticalAlign: "middle"}}></i>}
				{data.type ? <TypeBadge>{data.type}</TypeBadge> : null}
			</h3>
			<Text className="mb-3">{data.description}</Text>
			{data.items?.map((item, i) => (
				<Attribute key={i} data={item} basepath={basepath} />
			))}
		</div>
	)
}

const Attribute = ({data, basepath}) => {
	const link = `#/${basepath}.${data.path}`

	function copyLink(){
		copyText(new URL(link, window.location.href).href)
	}
	return (
		<div className="card mb-3">
			<div className="card-body">
				<h5 className="card-title">
					{data.path ? (
						<a href={link}
							className="text-decoration-none text-reset"
							onClick={copyLink}
						>
							<i className="fa-solid fa-link me-1" style={{fontSize: "0.75em"}}></i>
							<code>{data.title}</code>
						</a>
					) : (
						<code className="text-reset">{data.title}</code>
					)}
					{data.type ? <TypeBadge>{data.type}</TypeBadge> : null}
				</h5>
				<div className="card-text">
					{data.description ? <Text>{data.description}</Text> : null}
					{data.code ? (
						<div className="position-relative mt-2">
							<Code lang={data.lang}>{data.code}</Code>
							{data.lang == "python" ? (
								<button className="btn btn-sm btn-outline-success position-absolute"
									style={{top: "5px", right: "5px"}}
									onClick={_=>copyText(data.code)}
								>
									<i className="fa-solid fa-clone"></i>
								</button>
							) : null}
						</div>
					) : null}
					{data.output ? (
						<details className="mt-2">
							<summary className="btn btn-sm btn-outline-success">
								<i className="fas fa-play"></i> Execute
							</summary>
							<div className="output-box border rounded p-2 mt-2">
								<strong>Output:</strong>
								<Code lang="javascript">{data.output}</Code>
							</div>
						</details>
					) : null}
				</div>
			</div>
		</div>
	)
}

const TypeBadge = ({children}) => {
	const localTypes = {
		"HdRezkaFormat": "#/types.hdrezkaformat",
		"HdRezkaCategory": "#/types.hdrezkacategory",
		"HdRezkaRating": "#/types.hdrezkarating",
		"HdRezkaStream": "#/stream",
		"HdRezkaStreamSubtitles": "#/stream.subtitles",
		"SearchResult": "#/search.result",
	}
	return (
		<a
			className="badge rounded-pill text-bg-secondary font-monospace text-decoration-none ms-2"
			style={{fontSize: "0.75rem", verticalAlign: "middle"}}
			href={Object.keys(localTypes).includes(children) ? localTypes[children] : null}
		>
			{children}
		</a>
	)
}

function copyText(text) {
	const textArea = document.createElement("textarea");
	textArea.value = text;
	document.body.appendChild(textArea);
	textArea.select();
	document.execCommand('copy');
	document.body.removeChild(textArea);
}
