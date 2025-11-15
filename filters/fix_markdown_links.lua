if FORMAT:match("html") then
	function Link(elem)
		-- Don't replace remote markdowns
		if elem.target:match("^https?://") then
			return elem
		end
		
		-- Replace local markdown links to html.
		local new_str = elem.target:gsub("(%.?%/?.*)(%.md)", "%1.html")
		elem.target = new_str
		return elem
	end
end
