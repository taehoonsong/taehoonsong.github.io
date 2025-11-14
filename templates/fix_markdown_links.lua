-- Filter images with this function if the target format is HTML
if FORMAT:match("html") then
	function Link(elem)
		-- Replace local markdown links to html.
		local new_str = elem.target:gsub("(%.*%/*)(.md)", "%1.html")
		elem.target = new_str
		return elem
	end
end
