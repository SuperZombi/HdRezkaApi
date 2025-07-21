const Text = ({ children, className = "" }) => {
	if (!children) return null;
	return (
		<div
			className={className}
			dangerouslySetInnerHTML={{
				__html: marked.parse(children)
			}}
		/>
	)
}

const Code = ({ children, lang = "plaintext", className = "" }) => {
	const ref = React.useRef();

	React.useEffect(() => {
		if (ref.current) {
			hljs.highlightElement(ref.current);
		}
	}, [children, lang]);

	return (
		<pre className={`mb-2 ${className}`}>
			<code ref={ref} className={`language-${lang}`}>
				{js_beautify(children)}
			</code>
		</pre>
	)
}
