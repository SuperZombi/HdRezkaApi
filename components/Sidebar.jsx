const Sidebar = ({ menu, current }) => {
	return (
		<div className="list-group mb-4 position-sticky" style={{top: "1rem"}}>
			{menu.map((item, index) => (
				<a
					key={index}
					href={`#/${item.path}`}
					className={
						`list-group-item list-group-item-action${current == item.path ? " active" : ""}`
					}
				>
					<i className={`fas ${item.icon} me-2`}></i>
					{item.title}
				</a>
			))}
		</div>
	)
}
