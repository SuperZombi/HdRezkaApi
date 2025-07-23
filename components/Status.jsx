const Loading = () => {
	return (
		<h1 className="h-100 d-flex justify-content-center align-items-center"
			style={{minHeight: "100px"}}
		>
			<i className="fa-solid fa-circle-notch fa-spin"></i>
		</h1>
	)
}
const NotFound = () => {
	return (
		<div className="text-center">
			<h1 style={{fontSize: "40pt"}}>
				<i className="fa-regular fa-face-frown"></i>
			</h1>
			<h1 style={{fontSize: "48pt"}}>404</h1>
			<h1>Not Found</h1>
		</div>
	)
}
