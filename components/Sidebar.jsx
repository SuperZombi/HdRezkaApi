const Sidebar = ({ menu }) => {
	return (
		<div className="list-group">
			{menu.map((item, index) => (
				<a
					key={index}
					href={`#/${item.path}`}
					className="list-group-item list-group-item-action"
				>
					<i className={`fas ${item.icon} me-2`}></i>
					{item.title}
				</a>
			))}
		</div>
	)
}
