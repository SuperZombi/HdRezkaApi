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
		<pre className={`mb-0 ${className}`}>
			<code ref={ref} className={`language-${lang}`}>
				{lang=="javascript" ? js_beautify(children, {"brace_style": "expand"}) : children}
			</code>
		</pre>
	)
}
