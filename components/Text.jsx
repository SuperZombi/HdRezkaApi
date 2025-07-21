const Text = ({ children, className = "" }) => {
	if (!children) return null;
	return (
		<div
			className={className}
			dangerouslySetInnerHTML={{
				__html: marked.parseInline(children)
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
				{lang=="javascript" ? js_beautify(children, {"keep_array_indentation": true}) : children}
			</code>
		</pre>
	)
}
