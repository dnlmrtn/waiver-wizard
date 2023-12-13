import { Link } from 'react-router-dom';

const MenuItems = ({ items, depthLevel }) => {
    const isExternalLink = items.url.startsWith('http') || items.url.startsWith('https');

    const handleExternalLinkClick = (url) => {
        window.open(url, '_blank');
    };

    return (
        <li>
            {items.submenu ? (
                <>{ }</>
            ) : (
                isExternalLink ?
                    <button onClick={() => handleExternalLinkClick(items.url)}>{items.title}</button> :
                    <Link to={items.url} className="link-button">{items.title}</Link>
            )}
        </li>
    );
};

export default MenuItems;