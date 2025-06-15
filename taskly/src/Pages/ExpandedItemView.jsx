import React from 'react';
import './ExpandedItemView.css';
import { motion } from 'framer-motion'; // 1. Import motion
import ItemContent from './ItemContent'; // Import the shared content

// 2. Accept layoutId as a prop
const ExpandedItemView = ({ item, onClose, layoutId }) => {
  return (
    <motion.div
      className="expanded-view-overlay"
      onClick={onClose}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* 3. The element that matches the grid item gets the layoutId */}
      <motion.div
        layoutId={layoutId}
        className="expanded-view-content"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Render the same shared content component */}
        <ItemContent item={item} />

        {/* You can add extra details that only appear when expanded */}
        <motion.div
          className="expanded-only-details"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1, transition: { delay: 0 } }}
          exit={{ opacity: 0 }}
        >
          <p>This is extra information you only see in the expanded view.</p>
          <p>It fades in smoothly after the main animation.</p>
        </motion.div>

        <motion.button className="close-button" onClick={onClose}>
          x
        </motion.button>
      </motion.div>
    </motion.div>
  );
};

export default ExpandedItemView;